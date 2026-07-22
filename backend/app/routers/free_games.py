"""
routers/free_games.py — FreeToGame endpoints.

Endpoints:
  GET /api/free-games        — list of free-to-play games
  GET /api/free-games/{id}   — detailed info for a single game
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.services import free_games_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/free-games",
    summary="Free-to-play games",
    description=(
        "Returns a list of free-to-play games from FreeToGame. "
        "Supports platform and category filters. Cached 30 minutes."
    ),
)
async def list_free_games(
    platform: Optional[str] = Query(
        default=None,
        description="Filter by platform: 'pc' | 'browser' | 'all'",
    ),
    category: Optional[str] = Query(
        default=None,
        description="Filter by genre/category (e.g., 'mmorpg', 'shooter', 'strategy')",
    ),
    sort_by: Optional[str] = Query(
        default=None,
        description="Sort by: 'release-date' | 'popularity' | 'alphabetical' | 'relevance'",
    ),
    tag: Optional[str] = Query(default=None, description="Filter by tag"),
):
    try:
        games = await free_games_service.get_free_games(
            platform=platform,
            category=category,
            sort_by=sort_by,
            tag=tag,
        )
        return {"results": games, "count": len(games)}
    except Exception as exc:
        logger.error("list_free_games failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"FreeToGame API error: {str(exc)}",
        )


@router.get(
    "/free-games/{game_id}",
    summary="Free-to-play game detail",
    description="Returns detailed information for a single free-to-play game. Cached 30 minutes.",
)
async def get_free_game(game_id: int):
    try:
        return await free_games_service.get_free_game_detail(game_id)
    except Exception as exc:
        import httpx
        if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Free game {game_id} not found",
            )
        logger.error("get_free_game failed for id %d: %s", game_id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"FreeToGame API error: {str(exc)}",
        )
