"""
routers/news.py — Gaming news aggregation endpoint.

Endpoints:
  GET /api/news — merged gaming news from NewsAPI + NewsData.io

Results are fetched in parallel from both sources, normalised into
a common shape, deduplicated by title, and sorted newest-first.
Cached for 10 minutes.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.services import news_service

logger = logging.getLogger(__name__)
router = APIRouter()

_DEFAULT_QUERY = "gaming OR video games OR esports OR PC games OR PlayStation OR Xbox OR Nintendo"


@router.get(
    "/news",
    summary="Gaming news",
    description=(
        "Returns merged gaming news from NewsAPI and NewsData.io. "
        "Articles are deduplicated, normalised to a consistent shape, "
        "and sorted newest-first. Cached 10 minutes."
    ),
)
async def get_news(
    q: Optional[str] = Query(
        default=None,
        description="Custom search query. Defaults to a broad gaming query.",
    ),
    page_size: int = Query(
        default=50,
        ge=1,
        le=100,
        description="Number of articles to request from each source before merging.",
    ),
):
    try:
        query = q or _DEFAULT_QUERY
        result = await news_service.get_gaming_news(query=query, page_size=page_size)
        return result
    except Exception as exc:
        logger.error("get_news failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"News aggregation error: {str(exc)}",
        )
