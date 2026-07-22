"""
services/news_service.py — Gaming news aggregation from NewsAPI + NewsData.io.

Fetches from both sources in parallel, normalises each article into a
consistent NewsArticle shape, deduplicates by title, and returns a
merged list sorted by publication date (newest first).

API docs:
  NewsAPI:    https://newsapi.org/docs
  NewsData:   https://newsdata.io/docs
"""

import asyncio
import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from config import settings
from app.cache.memory_cache import cache
from app.utils.helpers import build_cache_key, truncate_text

logger = logging.getLogger(__name__)

# ── Cache TTLs ────────────────────────────────────────────────────────────────
TTL_NEWS = 10 * 60  # 10 minutes

# ── Gaming keywords for query ─────────────────────────────────────────────────
DEFAULT_QUERY = "gaming OR video games OR esports OR PC games OR PlayStation OR Xbox OR Nintendo"


# ── Internal fetch helpers ────────────────────────────────────────────────────

async def _fetch_newsapi(query: str = DEFAULT_QUERY, page_size: int = 50) -> List[Dict]:
    """Fetch articles from NewsAPI /v2/everything."""
    if not settings.news_api_key:
        logger.warning("NEWS_API_KEY not set — skipping NewsAPI")
        return []

    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": settings.news_api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.get("https://newsapi.org/v2/everything", params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("articles", [])
    except Exception as exc:
        logger.warning("NewsAPI fetch failed: %s", exc)
        return []


async def _fetch_newsdata(query: str = "gaming", page_size: int = 50) -> List[Dict]:
    """Fetch articles from NewsData.io /api/1/news."""
    if not settings.newsdata_api_key:
        logger.warning("NEWSDATA_API_KEY not set — skipping NewsData.io")
        return []

    params = {
        "q": query,
        "language": "en",
        "category": "technology,entertainment",
        "apikey": settings.newsdata_api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.get("https://newsdata.io/api/1/news", params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("results", [])
    except Exception as exc:
        logger.warning("NewsData.io fetch failed: %s", exc)
        return []


# ── Normalisation ─────────────────────────────────────────────────────────────

def _normalize_newsapi(article: Dict) -> Optional[Dict]:
    """Map a raw NewsAPI article to our internal shape."""
    title = (article.get("title") or "").strip()
    if not title or title == "[Removed]":
        return None

    source = article.get("source", {})
    return {
        "article_id": hashlib.md5(title.encode()).hexdigest(),
        "title": title,
        "description": truncate_text(article.get("description"), 300),
        "content": article.get("content"),
        "url": article.get("url"),
        "url_to_image": article.get("urlToImage"),
        "published_at": article.get("publishedAt"),
        "source": {"id": source.get("id"), "name": source.get("name")},
        "author": article.get("author"),
        "category": None,
        "provider": "newsapi",
    }


def _normalize_newsdata(article: Dict) -> Optional[Dict]:
    """Map a raw NewsData.io article to our internal shape."""
    title = (article.get("title") or "").strip()
    if not title:
        return None

    source_name = article.get("source_id") or article.get("source_name")
    image = article.get("image_url") or (
        article.get("multimedia", [{}])[0].get("url")
        if article.get("multimedia") else None
    )
    categories = article.get("category", [])
    category = categories[0] if categories else None

    return {
        "article_id": article.get("article_id") or hashlib.md5(title.encode()).hexdigest(),
        "title": title,
        "description": truncate_text(article.get("description"), 300),
        "content": article.get("content"),
        "url": article.get("link"),
        "url_to_image": image,
        "published_at": article.get("pubDate"),
        "source": {"id": source_name, "name": source_name},
        "author": (
            article.get("creator", [None])[0]
            if isinstance(article.get("creator"), list)
            else article.get("creator")
        ),
        "category": category,
        "provider": "newsdata",
    }


def _sort_key(article: Dict) -> datetime:
    """Parse published_at for sorting (newest first). Fallback to epoch if unparseable."""
    raw = article.get("published_at") or ""
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(raw[:19], fmt[:len(raw[:19])])
        except (ValueError, TypeError):
            continue
    return datetime(1970, 1, 1)


# ── Public Service Function ───────────────────────────────────────────────────

async def get_gaming_news(
    query: str = DEFAULT_QUERY,
    page_size: int = 50,
) -> Dict:
    """
    Fetch, merge, deduplicate, and sort gaming news from all sources.

    Returns a dict with:
        articles     — list of normalised article dicts
        total_results — count
        sources      — which APIs contributed
        fetched_at   — ISO timestamp
    """
    cache_key = build_cache_key("news", "gaming", query[:40], page_size)

    async def _fetch_and_merge():
        # Fetch from both APIs in parallel
        newsapi_raw, newsdata_raw = await asyncio.gather(
            _fetch_newsapi(query, page_size),
            _fetch_newsdata("gaming", page_size),
        )

        # Normalise
        articles = []
        for raw in newsapi_raw:
            norm = _normalize_newsapi(raw)
            if norm:
                articles.append(norm)

        for raw in newsdata_raw:
            norm = _normalize_newsdata(raw)
            if norm:
                articles.append(norm)

        # Deduplicate by lowercased title
        seen_titles: set = set()
        unique: List[Dict] = []
        for a in articles:
            key = a["title"].lower()[:80]
            if key not in seen_titles:
                seen_titles.add(key)
                unique.append(a)

        # Sort newest first
        unique.sort(key=_sort_key, reverse=True)

        sources = []
        if newsapi_raw:
            sources.append("newsapi")
        if newsdata_raw:
            sources.append("newsdata")

        return {
            "articles": unique,
            "total_results": len(unique),
            "sources": sources,
            "fetched_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

    return await cache.get_or_set(cache_key, _fetch_and_merge, ttl=TTL_NEWS)
