import re

with open(r'c:\Users\hungt\Documents\GitHub\COS30043_Final_Project\backend\app\services\itad_service.py', 'r', encoding='utf-8') as f:
    text = f.read()

# The logic replaces lines 61-94 with cache check for UUID
old_logic = '''            # ── 1. Lookup Game ID on ITAD ────────────────────────────────────
            itad_game = None

            # Try by Steam App ID first
            if steam_id:
                try:
                    resp = await client.get(
                        f"{ITAD_BASE_URL}/games/lookup/v1",
                        params={"key": api_key, "appid": steam_id},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        itad_game = data.get("game")
                except Exception as e:
                    logger.debug("ITAD lookup by appid %s failed: %s", steam_id, e)

            # Fallback to title lookup if appid failed or wasn't available
            if not itad_game and title:
                try:
                    resp = await client.get(
                        f"{ITAD_BASE_URL}/games/lookup/v1",
                        params={"key": api_key, "title": title},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        itad_game = data.get("game")
                except Exception as e:
                    logger.debug("ITAD lookup by title %s failed: %s", title, e)

            if not itad_game or not itad_game.get("id"):
                return None

            game_uuid = itad_game["id"]
            game_slug = itad_game.get("slug", "")'''

new_logic = '''            # ── 1. Lookup Game ID on ITAD ────────────────────────────────────
            itad_game = None
            uuid_cache_key = build_cache_key("itad_uuid", steam_id or "", title or "")
            cached_uuid_info = cache.get(uuid_cache_key)

            if cached_uuid_info:
                itad_game = cached_uuid_info
            else:
                # Try by Steam App ID first
                if steam_id:
                    try:
                        resp = await client.get(
                            f"{ITAD_BASE_URL}/games/lookup/v1",
                            params={"key": api_key, "appid": steam_id},
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            itad_game = data.get("game")
                    except Exception as e:
                        logger.debug("ITAD lookup by appid %s failed: %s", steam_id, e)

                # Fallback to title lookup if appid failed or wasn't available
                if not itad_game and title:
                    try:
                        resp = await client.get(
                            f"{ITAD_BASE_URL}/games/lookup/v1",
                            params={"key": api_key, "title": title},
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            itad_game = data.get("game")
                    except Exception as e:
                        logger.debug("ITAD lookup by title %s failed: %s", title, e)

                if itad_game and itad_game.get("id"):
                    # Cache the UUID mapping for 7 days to avoid repeated lookups
                    cache.set(uuid_cache_key, itad_game, ttl=604800)

            if not itad_game or not itad_game.get("id"):
                return None

            game_uuid = itad_game["id"]
            game_slug = itad_game.get("slug", "")'''

if old_logic in text:
    text = text.replace(old_logic, new_logic)
    with open(r'c:\Users\hungt\Documents\GitHub\COS30043_Final_Project\backend\app\services\itad_service.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated itad_service.py")
else:
    print("Could not find ITAD logic")
