"""
utils/helpers.py — Shared utility functions used across services and routers.
"""

import re
from typing import Any, Optional


def safe_get(data: Any, *keys, default=None) -> Any:
    """
    Safely traverse a nested dict/list with dot-path keys.

    Example:
        safe_get(response, "data", "results", 0, "name")
        # equivalent to: response["data"]["results"][0]["name"]
        # returns default if any key is missing or wrong type
    """
    current = data
    for key in keys:
        try:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, (list, tuple)):
                current = current[key]
            else:
                return default
        except (KeyError, IndexError, TypeError):
            return default
    return current


def truncate_text(text: Optional[str], max_length: int = 300, suffix: str = "...") -> Optional[str]:
    """
    Truncate *text* to at most *max_length* characters, appending *suffix* if truncated.
    Returns None if text is None.
    """
    if text is None:
        return None
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)].rstrip() + suffix


def normalize_url(url: Optional[str]) -> Optional[str]:
    """
    Ensure a URL starts with https://. Returns None if url is falsy.
    """
    if not url:
        return None
    url = url.strip()
    if url.startswith("//"):
        return "https:" + url
    if not url.startswith("http"):
        return "https://" + url
    return url


def strip_html(text: Optional[str]) -> Optional[str]:
    """
    Remove HTML tags from a string. Used when RAWG returns description_raw
    with embedded markup.
    """
    if not text:
        return text
    return re.sub(r"<[^>]+>", "", text).strip()


def build_cache_key(*parts) -> str:
    """
    Build a consistent cache key from positional parts.

    Example:
        build_cache_key("rawg", "game", 3498) → "rawg:game:3498"
    """
    return ":".join(str(p) for p in parts)


def clamp(value: int, min_val: int, max_val: int) -> int:
    """Clamp an integer between min_val and max_val."""
    return max(min_val, min(max_val, value))
