"""
routers/deals.py — CheapShark game deal endpoints.

Endpoints:
  GET /api/deals        — paginated deals with filter/sort options
  GET /api/deals/stores — list of supported stores
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.services import cheapshark_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/deals",
    summary="Game deals",
    description=(
        "Returns a list of game deals from CheapShark. "
        "Supports filtering by price, savings %, and store. "
        "Results are cached server-side for 15 minutes."
    ),
)
async def get_deals(
    page: int = Query(default=0, ge=0, description="Page number (0-indexed for CheapShark)"),
    page_size: int = Query(default=60, ge=1, le=60, description="Items per page (max 60)"),
    sort_by: str = Query(
        default="DealRating",
        description="Sort by: DealRating | Title | Savings | Price | MetacriticScore | Reviews | Release | Store | recent",
    ),
    upper_price: Optional[float] = Query(default=None, ge=0, description="Maximum deal price"),
    lower_price: Optional[float] = Query(default=None, ge=0, description="Minimum deal price"),
    min_savings: Optional[int] = Query(default=None, ge=0, le=100, description="Minimum savings percentage (0-100)"),
    store_id: Optional[str] = Query(default=None, description="Filter to a specific store ID"),
):
    try:
        deals = await cheapshark_service.get_deals(
            page_number=page,
            page_size=page_size,
            sort_by=sort_by,
            upper_price=upper_price,
            lower_price=lower_price,
            min_savings=min_savings,
            store_id=store_id,
        )
        return {
            "results": deals,
            "count": len(deals),
            "page": page,
            "page_size": page_size,
        }
    except Exception as exc:
        logger.error("get_deals failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"CheapShark API error: {str(exc)}",
        )


@router.get(
    "/deals/stores",
    summary="List deal stores",
    description="Returns the list of all supported stores from CheapShark. Cached for 1 hour.",
)
async def get_stores():
    try:
        return await cheapshark_service.get_stores()
    except Exception as exc:
        logger.error("get_stores failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"CheapShark stores error: {str(exc)}",
        )
