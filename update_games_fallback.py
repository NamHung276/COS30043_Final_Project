import re

with open(r'c:\Users\hungt\Documents\GitHub\COS30043_Final_Project\backend\app\routers\games.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add import cache
if 'from app.cache.memory_cache import cache' not in text:
    text = text.replace('from app.schemas.game import UnifiedGameDetail, GameSummary, Screenshot, Trailer', 'from app.cache.memory_cache import cache\nfrom app.schemas.game import UnifiedGameDetail, GameSummary, Screenshot, Trailer')

# 2. Add fallback ID mapping logic
old_logic = '''        steam_id = _extract_steam_app_id(detail)
        game_name = detail.get("name", f"Game #{game_id}")'''

new_logic = '''        # Fallback ID cache
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
            game_name = game_name or f"Game #{game_id}"'''

text = text.replace(old_logic, new_logic)

with open(r'c:\Users\hungt\Documents\GitHub\COS30043_Final_Project\backend\app\routers\games.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated games.py fallback mapping')
