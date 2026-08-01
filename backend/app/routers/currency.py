from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, Optional
import logging

from app.services import currency_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get(
    "/currency/list",
    summary="Get all supported currencies",
    description="Returns a dictionary of currency codes and their full names.",
)
async def get_currency_list() -> Dict[str, str]:
    try:
        data = await currency_service.get_currencies()
        if not data:
            raise HTTPException(status_code=503, detail="Currency service unavailable")
        return data
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to fetch currency list: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch currencies")

@router.get(
    "/currency/convert",
    summary="Convert currency",
    description="Convert an amount from one currency to another using real-time rates.",
)
async def convert_currency(
    from_curr: str = Query("USD", description="Currency to convert from (e.g. USD)"),
    to_curr: str = Query(..., description="Currency to convert to (e.g. EUR)"),
    amount: float = Query(1.0, description="Amount to convert"),
) -> Dict[str, Any]:
    try:
        data = await currency_service.convert_currency(from_curr, to_curr, amount)
        if not data:
            raise HTTPException(status_code=400, detail=f"Invalid currency pair or service unavailable: {from_curr} -> {to_curr}")
        return data
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to convert currency: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to convert currency")
