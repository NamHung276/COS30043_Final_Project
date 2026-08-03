"""
routers/games.py — RAWG game endpoints with CheapShark deal aggregation.

Endpoints:
  GET /api/games              — paginated game list
  GET /api/games/search       — search games by name
  GET /api/games/{id}         — aggregated game detail (RAWG + CheapShark + media)
  GET /api/games/{id}/screenshots — game screenshots
  GET /api/games/{id}/trailers    — game trailers / clips

The aggregated /api/games/{id} endpoint is the key value-add:
  It replaces 3 separate frontend API calls (detail, screenshots, trailers,
  plus a CheapShark lookup) with a single backend request.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, cast

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query, status
import re

from app.services import (
    rawg_service,
    cheapshark_service,
    ggdeals_service,
    steam_service,
    steamcharts_service,
    itad_service,
    youtube_service,
)
from app.services.recommendation_service import recommendation_service
from app.cache.memory_cache import cache
from app.schemas.game import UnifiedGameDetail, GameSummary, Screenshot, Trailer
from app.schemas.common import RAWGPaginatedResponse

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Helper ─────────────────────────────────────────────────────────────────────


def _rawg_error(exc: Exception, game_id: Optional[int] = None) -> HTTPException:
    """Convert an httpx error into a FastAPI HTTPException with a clear message."""
    import httpx

    # If it's already an HTTPException (e.g. 504 timeout from rawg_service), bubble it up
    if isinstance(exc, HTTPException):
        return exc

    if isinstance(exc, httpx.HTTPStatusError):
        if exc.response.status_code == 404:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game {game_id} not found on RAWG",
            )
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"RAWG API error: {exc.response.status_code}",
        )
    raise HTTPException(status_code=500, detail="Internal server error connecting to game APIs")

def _extract_steam_app_id(game_detail: dict) -> Optional[str]:
    """Helper to extract Steam App ID from RAWG stores array."""
    stores = game_detail.get("stores", [])
    for s in stores:
        store_info = s.get("store", {})
        if store_info.get("slug") == "steam" or store_info.get("id") == 1:
            url = s.get("url", "")
            if "/app/" in url:
                match = re.search(r'/app/(\d+)', url)
                if match:
                    return match.group(1)
    return None

# ── Endpoints ──────────────────────────────────────────────────────────────────


@router.get(
    "/games",
    response_model=RAWGPaginatedResponse[GameSummary],
    summary="List games",
    description=(
        "Returns a paginated list of games from RAWG. "
        "Results are cached server-side for 5 minutes. "
        "The RAWG API key is never exposed to the client."
    ),
)
async def list_games(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(
        default=20, ge=1, le=40, description="Items per page (max 40)"
    ),
    ordering: str = Query(
        default="-rating", description="Sort order (e.g., -rating, -released, name)"
    ),
    genres: Optional[str] = Query(
        default=None, description="Comma-separated genre slugs"
    ),
    platforms: Optional[str] = Query(
        default=None, description="Comma-separated platform IDs"
    ),
    tags: Optional[str] = Query(default=None, description="Comma-separated tag slugs"),
    dates: Optional[str] = Query(default=None, description="Comma-separated start and end date e.g. 2026-01-01,2026-12-31"),
    search: Optional[str] = Query(default=None, description="Search query"),
    exclude_additions: Optional[bool] = Query(default=None, description="Exclude DLCs"),
    metacritic: Optional[str] = Query(default=None, description="Metacritic range"),
    ratings_count: Optional[int] = Query(default=None, description="Min ratings count"),
):
    try:
        data = await rawg_service.get_games(
            page=page,
            page_size=page_size,
            ordering=ordering,
            genres=genres,
            platforms=platforms,
            tags=tags,
            dates=dates,
            search=search,
            exclude_additions=exclude_additions,
            metacritic=metacritic,
            ratings_count=ratings_count,
        )
        return data
    except Exception as exc:
        logger.error("list_games failed: %s", exc)
        raise _rawg_error(exc)


@router.get(
    "/games/search",
    response_model=RAWGPaginatedResponse[GameSummary],
    summary="Search games",
    description="Search games by name. Results cached for 5 minutes.",
)
async def search_games(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=40),
):
    try:
        return await rawg_service.search_games(query=q, page=page, page_size=page_size)
    except Exception as exc:
        logger.error("search_games failed for query '%s': %s", q, exc)
        raise _rawg_error(exc)


@router.get(
    "/games/recommendations",
    summary="Personalized recommendations",
    description="Returns personalized games by analyzing user activity.",
)
async def get_recommendations(
    user_id: Optional[str] = Query(default=None, description="Firebase User ID")
):
    try:
        if not user_id:
            # Fallback to generic recommendations if no user is provided
            return await recommendation_service._get_generic_recommendations()
        return await recommendation_service.get_recommendations(user_id)
    except Exception as exc:
        logger.error("get_recommendations failed for user %s: %s", user_id, exc)
        # Return empty list instead of failing
        return {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }


@router.get(
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

        detail = detail_res if not isinstance(detail_res, BaseException) else {}
        if not detail and isinstance(detail_res, BaseException):
            logger.warning(f"RAWG failed completely for {game_id}")
            
        screenshots_data = screenshots_res if not isinstance(screenshots_res, BaseException) else {}
        trailers_data = trailers_res if not isinstance(trailers_res, BaseException) else {}

        rawg_screenshots = screenshots_data.get("results", []) if isinstance(screenshots_data, dict) else []
        rawg_trailers = trailers_data.get("results", []) if isinstance(trailers_data, dict) else []

        # Fallback ID cache
        fallback_key = f"rawg_fallback_{game_id}"
        
        steam_id = _extract_steam_app_id(detail)
        game_name = detail.get("name")
        
        if steam_id and game_name:
            # Cache the successful mapping for 7 days
            cache.set(fallback_key, {"steam_id": steam_id, "name": game_name}, ttl=604800)
        elif not detail:
            # RAWG failed completely. Attempt to recover IDs from cache.
            cached_fallback = cache.get(fallback_key)
            if cached_fallback:
                steam_id = cached_fallback.get("steam_id")
                game_name = cached_fallback.get("name")
                logger.info(f"Recovered missing RAWG data from cache for {game_id}")
            else:
                game_name = f"Game #{game_id}"
        else:
            game_name = game_name or f"Game #{game_id}"

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

        cs_res = secondary_results[0] if not isinstance(secondary_results[0], BaseException) else []
        gg_bundles = secondary_results[1] if not isinstance(secondary_results[1], BaseException) and secondary_results[1] else {}
        steam_data = secondary_results[2] if not isinstance(secondary_results[2], BaseException) and secondary_results[2] else {}
        charts_data = secondary_results[3] if not isinstance(secondary_results[3], BaseException) and secondary_results[3] else {}
        itad_data = secondary_results[4] if not isinstance(secondary_results[4], BaseException) and secondary_results[4] else {}
        yt_trailer = secondary_results[5] if not isinstance(secondary_results[5], BaseException) else None

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
                    "initial": float(cs_best.get("normalPrice") or cs_val),
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
                "initial": float(cs_best.get("normalPrice") or cs_best.get("cheapest", 0)),
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

@router.get(
    "/games/{game_id}/screenshots",
    response_model=RAWGPaginatedResponse[Screenshot],
    summary="Game screenshots",
    description="Returns screenshot images for the given game. Cached 10 minutes.",
)
async def get_game_screenshots(game_id: int):
    try:
        return await rawg_service.get_screenshots(game_id)
    except Exception as exc:
        logger.error("get_screenshots failed for game %d: %s", game_id, exc)
        raise _rawg_error(exc, game_id)


@router.get(
    "/games/{game_id}/trailers",
    response_model=RAWGPaginatedResponse[Trailer],
    summary="Game trailers",
    description="Returns trailer/clip data for the given game. Cached 10 minutes.",
)
async def get_game_trailers(game_id: int):
    try:
        return await rawg_service.get_trailers(game_id)
    except Exception as exc:
        logger.error("get_trailers failed for game %d: %s", game_id, exc)
        raise _rawg_error(exc, game_id)

class SysReqTranslationRequest(BaseModel):
    text: str

@router.post(
    "/games/format-sysreq",
    summary="Format System Requirements",
    description="Format system requirements text and use AI translation if it is non-English."
)
async def format_sysreq(req: SysReqTranslationRequest):
    from app.services import ai_service
    prompt = f"""
    You are a game system requirements formatter. 
    Analyze the following system requirements text:
    - If it contains 2 languages (e.g. English and Chinese), create a paragraph gap between them.
    - If it is 1 language but NOT English, translate it to English.
    - Format the text to make it easy to read using Markdown bullet points (like 'OS:', 'Processor:', etc).
    - Do not add any extra commentary or introductory text, just return the formatted requirements as clean HTML (using <ul>, <li>, and <strong> tags).
    
    Text:
    {req.text}
    """
    try:
        formatted = await ai_service.generate_response(prompt)
        # Gemini sometimes wraps HTML in ```html ... ```, let's strip it.
        formatted = formatted.replace("```html", "").replace("```", "").strip()
        return {"formatted_text": formatted}
    except Exception as e:
        logger.error(f"Error formatting sysreq: {e}")
        return {"formatted_text": req.text}

@router.get(
    "/games/bundles/active",
    summary="Get active game bundles from GG.deals",
    description="Returns a list of currently active bundles across various stores.",
)
async def get_active_bundles(
    region: str = Query("us", description="Region code for pricing"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    offset: Optional[int] = Query(None, description="Pagination offset"),
):
    try:
        data = await ggdeals_service.get_active_bundles(region=region, cursor=cursor, offset=offset)
        if not data:
            return {"bundles": [], "totalCount": 0}
        return data
    except Exception as exc:
        logger.error(f"Failed to fetch active bundles: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch active bundles")
