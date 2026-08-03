"""
services/steamcharts_service.py — SteamCharts player count integration.

SteamCharts (steamcharts.com) provides live player count data for Steam games.
There is no official API — we parse the page's embedded JSON data.

This data is ADDITIVE — RAWG has no live player counts.
Returns None gracefully on any parse failure.
"""

import logging
import re
from typing import Any, Dict, Optional

import httpx

from app.cache.memory_cache import cache
from app.utils.helpers import build_cache_key

logger = logging.getLogger(__name__)

STEAMCHARTS_BASE = "https://steamcharts.com/app"

# Cache TTL: 30 minutes (player counts update every few minutes on SteamCharts,
# but we don't need to be real-time — 30 min is respectful to their servers)
TTL_PLAYER_COUNTS = 30 * 60


async def get_player_counts(steam_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch live player counts for a Steam game.

    Returns a dict with:
        - current   (int) — current players online
        - peak_24h  (int) — 24-hour peak
        - peak_all  (int) — all-time peak
        - source_url (str)

    Returns None on failure (network error, parse error, rate limit).
    The caller treats None as "SteamCharts section unavailable".
    """
    if not steam_id:
        return None

    cache_key = build_cache_key("steamcharts", "players", steam_id)

    async def _fetch() -> Optional[Dict[str, Any]]:
        url = f"{STEAMCHARTS_BASE}/{steam_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; GameHub/3.0; COS30043 Project)",
            "Accept": "text/html",
            "Accept-Language": "en-US,en;q=0.9",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, headers=headers, follow_redirects=True) as client:
                resp = await client.get(url)

                if resp.status_code in (404, 410):
                    # Game not on SteamCharts (console-only, etc.)
                    return None
                if resp.status_code == 429:
                    logger.warning("SteamCharts rate-limited for app %s", steam_id)
                    return None

                resp.raise_for_status()
                html = resp.text

                # ── Parse player counts from the stat boxes ─────────────────
                # SteamCharts embeds current/peak in elements like:
                # <span class="num">12,345</span>
                # We look for the known stat section structure.

                def _parse_num(text: str) -> Optional[int]:
                    """Convert '12,345' or '1.2m' to int."""
                    text = text.strip().replace(",", "")
                    if not text or text == "—":
                        return None
                    try:
                        return int(float(text))
                    except ValueError:
                        return None

                # Find all .app-stat span.num values in order:
                # [0] = current players, [1] = peak 24h, [2] = all-time peak
                nums = re.findall(
                    r'<span class="num">([0-9,\.]+)</span>',
                    html,
                )

                if len(nums) < 2:
                    # Page structure may have changed
                    logger.warning(
                        "SteamCharts: unexpected page structure for app %s (found %d nums)",
                        steam_id, len(nums),
                    )
                    return None

                current = _parse_num(nums[0]) if len(nums) > 0 else None
                peak_24h = _parse_num(nums[1]) if len(nums) > 1 else None
                peak_all = _parse_num(nums[2]) if len(nums) > 2 else None

                if current is None and peak_24h is None:
                    return None

                return {
                    "current": current,
                    "peak_24h": peak_24h,
                    "peak_all": peak_all,
                    "source_url": url,
                }

        except httpx.TimeoutException:
            logger.warning("SteamCharts timed out for app %s", steam_id)
            return None
        except httpx.HTTPStatusError as exc:
            logger.warning("SteamCharts HTTP %s for app %s", exc.response.status_code, steam_id)
            return None
        except Exception as exc:
            logger.warning("SteamCharts error for app %s: %s", steam_id, exc)
            return None

    try:
        return await cache.get_or_set(cache_key, _fetch, ttl=TTL_PLAYER_COUNTS)
    except Exception as exc:
        logger.warning("SteamCharts cache error for app %s: %s", steam_id, exc)
        return None
