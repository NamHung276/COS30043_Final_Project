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

from app.services import rawg_service, cheapshark_service, ggdeals_service
from app.services.recommendation_service import recommendation_service
from app.schemas.game import GameDetail, GameSummary, Screenshot, Trailer
from app.schemas.common import RAWGPaginatedResponse

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Helper ─────────────────────────────────────────────────────────────────────


def _rawg_error(exc: Exception, game_id: Optional[int] = None) -> HTTPException:
    """Convert an httpx error into a FastAPI HTTPException with a clear message."""
    import httpx

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
        raise _rawg_error(exc)


@router.get(
    "/games/{game_id}",
    response_model=GameDetail,
    summary="Aggregated game detail",
    description=(
        "**Aggregated endpoint.** Returns a single JSON object combining:\n"
        "- RAWG game detail (description, genres, platforms, developers, publishers)\n"
        "- RAWG screenshots\n"
        "- RAWG trailers\n"
        "- CheapShark deals (current sale prices across stores)\n\n"
        "Replaces 4 separate frontend API calls. Cached 10 minutes."
    ),
)
async def get_game_detail(game_id: int):
    try:
        # Fire all requests concurrently
        detail_task = rawg_service.get_game_detail(game_id)
        screenshots_task = rawg_service.get_screenshots(game_id)
        trailers_task = rawg_service.get_trailers(game_id)

        detail, screenshots_data, trailers_data = await asyncio.gather(
            detail_task,
            screenshots_task,
            trailers_task,
            return_exceptions=True,
        )

        # If the main detail call fails, surface the error
        if isinstance(detail, Exception):
            raise detail

        # Narrow type: detail is guaranteed to be a dict at this point
        detail = cast(Dict[str, Any], detail)

        # Non-fatal failures for supplementary data
        screenshots = []
        if not isinstance(screenshots_data, Exception):
            screenshots = cast(Dict[str, Any], screenshots_data).get("results", [])
        else:
            logger.warning(
                "Screenshots fetch failed for game %d: %s", game_id, screenshots_data
            )

        trailers = []
        if not isinstance(trailers_data, Exception):
            trailers = cast(Dict[str, Any], trailers_data).get("results", [])
        else:
            logger.warning(
                "Trailers fetch failed for game %d: %s", game_id, trailers_data
            )

        # Try to find CheapShark deals by game name (non-fatal)
        deals = []
        cheapest_price = None
        cheapest_store = None
        try:
            game_name = detail.get("name", "")
            cs_results = await cheapshark_service.get_deals_by_game_name(game_name)
            if cs_results:
                # cs_results is a list of {gameID, cheapest, cheapestDealID, external, ...}
                best = min(
                    cs_results,
                    key=lambda g: float(g.get("cheapest", "9999")),
                    default=None,
                )
                if best:
                    cheapest_price = best.get("cheapest")
                    # No easy storeID mapping from /games CheapShark endpoint
                    cheapest_store = None
                deals = cs_results
        except Exception as cs_exc:
            logger.warning("CheapShark lookup failed for game %d: %s", game_id, cs_exc)

        # Try to find GG.deals prices and bundles by Steam App ID
        ggdeals_data = None
        steam_id = _extract_steam_app_id(detail)
        if steam_id:
            try:
                results = await asyncio.gather(
                    ggdeals_service.get_prices_by_steam_id(steam_id),
                    ggdeals_service.get_bundles_by_steam_id(steam_id),
                    return_exceptions=True
                )
                prices_res = results[0] if isinstance(results[0], dict) else None
                bundles_res = results[1] if isinstance(results[1], dict) else None
                
                if prices_res or bundles_res:
                    fallback_dict = prices_res or bundles_res or {}
                    ggdeals_data = {
                        "url": fallback_dict.get("url"),
                        "prices": prices_res.get("prices") if prices_res else None,
                        "bundles": bundles_res.get("bundles") if bundles_res else []
                    }
            except Exception as gg_exc:
                logger.warning("GG.deals lookups failed for game %d (steam %s): %s", game_id, steam_id, gg_exc)

        # Assemble aggregated response
        return {
            **detail,
            "screenshots": screenshots,
            "trailers": trailers,
            "deals": deals,
            "ggdeals": ggdeals_data,
            "cheapest_deal_price": cheapest_price,
            "cheapest_deal_store": cheapest_store,
            "rawg_url": f"https://rawg.io/games/{detail.get('slug', game_id)}",
            "aggregated_at": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("get_game_detail failed for game %d: %s", game_id, exc)
        raise _rawg_error(exc, game_id)


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
