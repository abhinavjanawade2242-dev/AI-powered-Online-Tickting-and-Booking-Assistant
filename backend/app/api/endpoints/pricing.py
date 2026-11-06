from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.pricing_service import PricingService
from app.schemas import PriceQuoteRequest, PriceQuoteResponse

router = APIRouter(prefix="/pricing", tags=["Pricing Engine & Business Rules"])


@router.post("/quote", response_model=PriceQuoteResponse, summary="Pricing: Calculate quote with discounts and taxes")
async def calculate_price_quote(
    req: PriceQuoteRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Transparent Pricing Engine Quote Calculation.
    - Base: unit_price * quantity
    - Automatic Group Discount: 10% off for 4+ tickets
    - Validated Promo Codes: TECH20 (20% off), STUDENT10 (10% off), EARLYBIRD (₹50 flat), FREEPASS (100% waiver)
    - Full breakdown of fees, taxes, and final payable amount in INR (₹).
    """
    try:
        quote = await PricingService.get_tier_quote(
            db=db,
            tier_id=req.tier_id,
            quantity=req.quantity,
            promo_code=req.promo_code
        )
        return PriceQuoteResponse(
            unit_price=quote.unit_price,
            quantity=quote.quantity,
            base_amount=quote.base_amount,
            discount_amount=quote.discount_amount,
            discount_description=quote.discount_description,
            convenience_fee=quote.convenience_fee,
            tax_amount=quote.tax_amount,
            total_payable=quote.total_payable,
            currency=quote.currency,
            is_free=quote.is_free
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/tiers/{tier_id}", response_model=PriceQuoteResponse, summary="Pricing: Quick quote for a tier")
async def get_tier_price_quote(
    tier_id: str,
    quantity: int = Query(1, ge=1, le=10, description="Number of tickets"),
    promo_code: Optional[str] = Query(None, description="Optional coupon or promo code"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve live pricing breakdown for an event ticket tier.
    """
    try:
        quote = await PricingService.get_tier_quote(
            db=db,
            tier_id=tier_id,
            quantity=quantity,
            promo_code=promo_code
        )
        return PriceQuoteResponse(
            unit_price=quote.unit_price,
            quantity=quote.quantity,
            base_amount=quote.base_amount,
            discount_amount=quote.discount_amount,
            discount_description=quote.discount_description,
            convenience_fee=quote.convenience_fee,
            tax_amount=quote.tax_amount,
            total_payable=quote.total_payable,
            currency=quote.currency,
            is_free=quote.is_free
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/promos", summary="Pricing: List active promotional codes")
async def list_active_promos() -> List[Dict[str, Any]]:
    """
    Returns verified promotional discount codes for collegiate student hackathon demos.
    """
    return [
        {"code": code, **meta}
        for code, meta in PricingService.SUPPORTED_PROMOS.items()
    ]

