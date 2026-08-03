"""
services/youtube_service.py — YouTube Data API v3 trailer fallback.

Used ONLY when RAWG provides no trailer for a game.
If RAWG has a trailer, this service is never called.

Requires YOUTUBE_API_KEY environment variable.
If the key is not set, all functions return None silently.

YouTube Data API v3 docs: https://developers.google.com/youtube/v3
"""

import logging
from typing import Any, Dict, Optional

import httpx

from config import settings
from app.cache.memory_cache import cache
from app.utils.helpers import build_cache_key

logger = logging.getLogger(__name__)

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

# Cache TTL: 60 minutes (trailer results are stable)
TTL_YOUTUBE = 60 * 60


async def search_game_trailer(game_name: str) -> Optional[str]:
    """
    Search YouTube for an official game trailer.

    Returns the YouTube video ID (e.g. "dQw4w9WgXcQ") or None.

    Priority:
      1. RAWG trailers always take precedence — this is only a fallback.
      2. Search query: "{game_name} official trailer"
      3. Returns the top result's video ID.

    Returns None if:
      - YOUTUBE_API_KEY is not configured
      - No results found
      - API request fails
    """
    api_key = settings.youtube_api_key
    if not api_key:
        return None

    if not game_name:
        return None

    cache_key = build_cache_key("youtube", "trailer", game_name.lower().strip())

    async def _fetch() -> Optional[str]:
        query = f"{game_name} official trailer"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": 3,
            "videoEmbeddable": "true",
            "videoCategoryId": "20",  # Gaming category
            "key": api_key,
        }
        headers = {
            "User-Agent": "GameHub/3.0 (COS30043 University Project)",
            "Accept": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
                resp = await client.get(f"{YOUTUBE_API_BASE}/search", params=params)

                if resp.status_code == 403:
                    logger.warning("YouTube API quota exceeded or key invalid")
                    return None
                if resp.status_code == 400:
                    logger.warning("YouTube API bad request for query: %s", query)
                    return None

                resp.raise_for_status()
                data = resp.json()

                items = data.get("items", [])
                if not items:
                    return None

                # Prefer results with "official" or "trailer" in the title
                for item in items:
                    title = item.get("snippet", {}).get("title", "").lower()
                    video_id = item.get("id", {}).get("videoId")
                    if video_id and ("official" in title or "trailer" in title):
                        return video_id

                # Fallback to first result
                first_id = items[0].get("id", {}).get("videoId")
                return first_id

        except httpx.TimeoutException:
            logger.warning("YouTube API timed out for game: %s", game_name)
            return None
        except httpx.HTTPStatusError as exc:
            logger.warning("YouTube API HTTP %s for game: %s", exc.response.status_code, game_name)
            return None
        except Exception as exc:
            logger.warning("YouTube API error for game %s: %s", game_name, exc)
            return None

    try:
        return await cache.get_or_set(cache_key, _fetch, ttl=TTL_YOUTUBE)
    except Exception as exc:
        logger.warning("YouTube cache error for game %s: %s", game_name, exc)
        return None
