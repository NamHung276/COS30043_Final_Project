"""
memory_cache.py — Simple TTL-based in-memory cache.

No external dependencies. Thread-safe using threading.Lock.
Can be swapped for Redis in production without changing any service code.

Usage:
    from app.cache.memory_cache import cache

    cache.set("my_key", {"data": [...]}, ttl=300)
    result = cache.get("my_key")   # None if expired or missing
    cache.invalidate("my_key")
    cache.clear()
"""

import logging
import threading
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)


class MemoryCache:
    """
    Thread-safe in-memory cache with per-entry TTL (time-to-live).

    Each entry stores:
        - value:      the cached data
        - expires_at: Unix timestamp when the entry expires
    """

    def __init__(self) -> None:
        self._store: dict[str, dict] = {}
        self._lock = threading.Lock()

    # ── Public API ───────────────────────────────────────────────────────────────

    def get(self, key: str) -> Optional[Any]:
        """
        Return the cached value for *key*, or None if missing / expired.
        Expired entries are lazily evicted on read.
        """
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None

            if time.monotonic() > entry["expires_at"]:
                # Lazy eviction — remove stale entry
                del self._store[key]
                logger.debug("Cache miss (expired): %s", key)
                return None

            logger.debug("Cache hit: %s", key)
            return entry["value"]

    def set(self, key: str, value: Any, ttl: int) -> None:
        """
        Store *value* under *key* with a TTL of *ttl* seconds.

        Args:
            key:   Cache key string.
            value: Any serialisable Python object.
            ttl:   Seconds until this entry expires (must be > 0).
        """
        if ttl <= 0:
            raise ValueError(f"TTL must be positive, got {ttl}")

        with self._lock:
            self._store[key] = {
                "value": value,
                "expires_at": time.monotonic() + ttl,
            }
            logger.debug("Cache set: %s (ttl=%ds)", key, ttl)

    def invalidate(self, key: str) -> bool:
        """
        Remove a specific entry. Returns True if the key existed.
        """
        with self._lock:
            existed = key in self._store
            self._store.pop(key, None)
            if existed:
                logger.debug("Cache invalidated: %s", key)
            return existed

    def clear(self) -> int:
        """
        Remove all entries. Returns the number of entries cleared.
        Useful for testing or forced refresh.
        """
        with self._lock:
            count = len(self._store)
            self._store.clear()
            logger.info("Cache cleared (%d entries removed)", count)
            return count

    def stats(self) -> dict:
        """Return diagnostic information about the cache."""
        with self._lock:
            now = time.monotonic()
            total = len(self._store)
            expired = sum(1 for e in self._store.values() if now > e["expires_at"])
            return {
                "total_entries": total,
                "live_entries": total - expired,
                "expired_entries": expired,
            }

    # ── Convenience: get-or-set pattern ──────────────────────────────────────────

    async def get_or_set(self, key: str, factory, ttl: int) -> Any:
        """
        Return cached value if present; otherwise call *factory* (async),
        cache the result, and return it.

        Args:
            key:     Cache key.
            factory: An async callable that produces the value on a cache miss.
            ttl:     Seconds to cache the new value.

        Example:
            data = await cache.get_or_set(
                "games:list",
                lambda: rawg_service.get_games(page=1),
                ttl=300,
            )
        """
        hit = self.get(key)
        if hit is not None:
            return hit

        value = await factory()
        self.set(key, value, ttl=ttl)
        return value


# ── Module-level singleton ─────────────────────────────────────────────────────
# Import this object directly:  from app.cache.memory_cache import cache
cache = MemoryCache()
