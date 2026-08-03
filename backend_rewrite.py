import re

with open(r'c:\Users\hungt\Documents\GitHub\COS30043_Final_Project\backend\app\routers\games.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace import
content = content.replace(
    "from app.schemas.game import GameDetail, GameSummary, Screenshot, Trailer",
    "from app.schemas.game import UnifiedGameDetail, GameSummary, Screenshot, Trailer"
)

# New get_game_detail function
new_func = """@router.get(
    "/games/{game_id}",
    response_model=UnifiedGameDetail,
    summary="Unified game detail",
    description="Returns a single unified JSON object combining RAWG, Steam, ITAD, CheapShark, and SteamCharts.",
)
async def get_game_detail(game_id: int):
    try:
        # Fire all requests concurrently
        detail_task = rawg_service.get_game_detail(game_id)
        screenshots_task = rawg_service.get_screenshots(game_id)
        trailers_task = rawg_service.get_trailers(game_id)

        detail_res, screenshots_res, trailers_res = await asyncio.gather(
            detail_task,
            screenshots_task,
            trailers_task,
            return_exceptions=True,
        )

        detail = detail_res if not isinstance(detail_res, Exception) else {}
        if not detail and isinstance(detail_res, Exception):
            logger.warning(f"RAWG failed completely for {game_id}")
            
        screenshots_data = screenshots_res if not isinstance(screenshots_res, Exception) else {}
        trailers_data = trailers_res if not isinstance(trailers_res, Exception) else {}

        rawg_screenshots = screenshots_data.get("results", []) if isinstance(screenshots_data, dict) else []
        rawg_trailers = trailers_data.get("results", []) if isinstance(trailers_data, dict) else []

        steam_id = _extract_steam_app_id(detail)
        game_name = detail.get("name", f"Game #{game_id}")

        # Now fetch secondary sources concurrently
        cs_task = cheapshark_service.get_deals_by_game_name(game_name)
        gg_bundles_task = ggdeals_service.get_bundles_by_steam_id(steam_id) if steam_id else asyncio.sleep(0)
        steam_task = steam_service.get_steam_app_details(steam_id) if steam_id else asyncio.sleep(0)
        charts_task = steamcharts_service.get_player_counts(steam_id) if steam_id else asyncio.sleep(0)
        itad_task = itad_service.get_itad_deals(steam_id=steam_id, title=game_name)
        
        has_rawg_trailer = bool(rawg_trailers) or bool(detail.get("clip"))
        yt_task = youtube_service.search_game_trailer(game_name) if not has_rawg_trailer else asyncio.sleep(0)

        secondary_results = await asyncio.gather(
            cs_task,
            gg_bundles_task,
            steam_task,
            charts_task,
            itad_task,
            yt_task,
            return_exceptions=True
        )

        cs_res = secondary_results[0] if not isinstance(secondary_results[0], Exception) else []
        gg_bundles = secondary_results[1] if not isinstance(secondary_results[1], Exception) and secondary_results[1] else {}
        steam_data = secondary_results[2] if not isinstance(secondary_results[2], Exception) and secondary_results[2] else {}
        charts_data = secondary_results[3] if not isinstance(secondary_results[3], Exception) and secondary_results[3] else {}
        itad_data = secondary_results[4] if not isinstance(secondary_results[4], Exception) and secondary_results[4] else {}
        yt_trailer = secondary_results[5] if not isinstance(secondary_results[5], Exception) else None

        # -- GAP FILLING LOGIC --

        # Title
        final_title = steam_data.get("title") or detail.get("name", f"Game #{game_id}")

        # Description
        final_desc = detail.get("description_raw") or steam_data.get("short_description") or "Description unavailable."

        # Hero Image
        final_hero = detail.get("background_image_additional") or detail.get("background_image") or steam_data.get("header_image")
        
        # Cover Image
        final_cover = detail.get("background_image") or steam_data.get("header_image")

        # Screenshots
        final_screenshots = [s.get("image") for s in rawg_screenshots if s.get("image")]
        if not final_screenshots and steam_data.get("screenshots"):
            final_screenshots = steam_data.get("screenshots")

        # Trailer
        final_trailer = None
        if rawg_trailers and rawg_trailers[0].get("data"):
            trailer_data = rawg_trailers[0].get("data", {})
            final_trailer = {
                "url": trailer_data.get("max") or trailer_data.get("480"),
                "poster": rawg_trailers[0].get("preview"),
                "is_youtube_fallback": False
            }
        elif detail.get("clip") and detail["clip"].get("clip"):
            final_trailer = {
                "url": detail["clip"]["clip"],
                "poster": detail["clip"].get("preview"),
                "is_youtube_fallback": False
            }
        elif yt_trailer:
            final_trailer = {
                "url": f"https://www.youtube.com/embed/{yt_trailer}",
                "poster": None,
                "is_youtube_fallback": True
            }

        # Price
        final_price = None
        itad_current = itad_data.get("current_best")
        
        cs_best = None
        if cs_res:
            valid_cs = []
            if steam_id:
                valid_cs = [g for g in cs_res if g.get("steamAppID") == steam_id]
            if not valid_cs:
                valid_cs = [g for g in cs_res if g.get("external", "").lower() == final_title.lower()]
            if valid_cs:
                cs_best = min(valid_cs, key=lambda g: float(g.get("cheapest", "9999")), default=None)

        if cs_best and itad_current:
            cs_val = float(cs_best.get("cheapest", 0))
            itad_val = float(itad_current.get("price", {}).get("amount", 9999))
            if cs_val <= itad_val:
                final_price = {
                    "currency": "USD",
                    "initial": float(cs_best.get("normalPrice", cs_val) or cs_val),
                    "final": cs_val,
                    "discount_percent": 0,
                    "store_name": "CheapShark",
                    "url": f"https://www.cheapshark.com/redirect?dealID={cs_best.get('dealID')}",
                    "source": "CheapShark"
                }
            else:
                final_price = {
                    "currency": itad_current.get("price", {}).get("currency", "USD"),
                    "initial": itad_current.get("regular", {}).get("amount", itad_val),
                    "final": itad_val,
                    "discount_percent": itad_current.get("cut", 0),
                    "store_name": itad_current.get("store", {}).get("name", "Unknown Store"),
                    "url": itad_current.get("url"),
                    "source": "ITAD"
                }
        elif itad_current:
            final_price = {
                "currency": itad_current.get("price", {}).get("currency", "USD"),
                "initial": itad_current.get("regular", {}).get("amount", itad_current.get("price", {}).get("amount", 0)),
                "final": itad_current.get("price", {}).get("amount", 0),
                "discount_percent": itad_current.get("cut", 0),
                "store_name": itad_current.get("store", {}).get("name", "Unknown Store"),
                "url": itad_current.get("url"),
                "source": "ITAD"
            }
        elif cs_best:
            final_price = {
                "currency": "USD",
                "initial": float(cs_best.get("normalPrice", cs_best.get("cheapest", 0))),
                "final": float(cs_best.get("cheapest", 0)),
                "discount_percent": 0,
                "store_name": "CheapShark",
                "url": f"https://www.cheapshark.com/redirect?dealID={cs_best.get('dealID')}",
                "source": "CheapShark"
            }
        elif steam_data and steam_data.get("price"):
            final_price = {
                "currency": steam_data["price"].get("currency", "USD"),
                "initial": steam_data["price"].get("initial", 0.0),
                "final": steam_data["price"].get("final", 0.0),
                "discount_percent": steam_data["price"].get("discount_percent", 0),
                "store_name": "Steam",
                "url": steam_data.get("steam_url"),
                "source": "Steam"
            }

        # Historical Low
        final_hist = None
        itad_hist = itad_data.get("historical_low")
        if itad_hist:
            final_hist = {
                "amount": itad_hist.get("price", {}).get("amount", 0),
                "store_name": itad_hist.get("store", {}).get("name", "Unknown Store"),
                "date": itad_hist.get("timestamp", ""),
                "url": None,
                "source": "ITAD"
            }

        # Players
        final_players = None
        if charts_data:
            final_players = {
                "live": charts_data.get("live_players", 0),
                "peak_24h": charts_data.get("peak_24h", 0),
                "peak_all_time": charts_data.get("peak_all_time", 0),
                "source": "SteamCharts"
            }

        return {
            "id": game_id,
            "title": final_title,
            "slug": detail.get("slug", str(game_id)),
            "description": final_desc,
            "hero_image": final_hero,
            "cover_image": final_cover,
            "released": detail.get("released"),
            "metacritic": detail.get("metacritic"),
            "website": detail.get("website"),
            "esrb_rating": detail.get("esrb_rating"),
            "screenshots": final_screenshots,
            "genres": [g.get("name") for g in detail.get("genres", []) if g.get("name")],
            "developers": [d.get("name") for d in detail.get("developers", []) if d.get("name")],
            "publishers": [p.get("name") for p in detail.get("publishers", []) if p.get("name")],
            "platforms": [p.get("platform", {}).get("name") for p in detail.get("platforms", []) if p.get("platform", {}).get("name")],
            "languages": steam_data.get("supported_languages", []),
            "categories": steam_data.get("categories", []),
            "achievements_total": steam_data.get("achievements_total", 0),
            "price": final_price,
            "historical_low": final_hist,
            "players": final_players,
            "trailer": final_trailer,
            "store_deals": itad_data.get("store_deals", []),
            "bundles": gg_bundles.get("bundles", []),
            "rawg_url": f"https://rawg.io/games/{detail.get('slug', game_id)}",
            "steam_url": steam_data.get("steam_url") if steam_data else None,
            "aggregated_at": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as exc:
        logger.error("get_game_detail failed for game %d: %s", game_id, exc)
        return {
            "id": game_id,
            "title": f"Game #{game_id}",
            "slug": str(game_id),
            "description": "Unable to load game details. Please try again later.",
            "aggregated_at": datetime.now(timezone.utc).isoformat(),
        }
"""

start_str = "@router.get("
start_idx = content.find(start_str, content.find('"/games/{game_id}"') - 50)
if start_idx == -1:
    print("Could not find start of get_game_detail")
    exit(1)

end_str = "@router.get("
end_idx = content.find(end_str, start_idx + 100)
if end_idx == -1:
    end_idx = len(content)

new_content = content[:start_idx] + new_func + "\n" + content[end_idx:]

with open(r'c:\Users\hungt\Documents\GitHub\COS30043_Final_Project\backend\app\routers\games.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Replaced get_game_detail successfully.")
