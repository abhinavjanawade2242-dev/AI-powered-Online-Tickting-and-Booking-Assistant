from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.inventory_service import InventoryService
from app.schemas import TicketTierAvailability

router = APIRouter(tags=["Stage 3: Availability"])


@router.get("/events/{event_id}/availability", summary="Availability: Live ticket inventory and tier prices")
async def get_event_availability(
    event_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Stage 3: Availability.
    System checks actual ticket inventory, dates, pricing tiers, and sold-out states.
    """
    try:
        return await InventoryService.get_event_inventory(db, event_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/tiers/{tier_id}/availability", response_model=TicketTierAvailability, summary="Check tier availability")
async def get_tier_availability(
    tier_id: str,
    db: AsyncSession = Depends(get_db)
):
    avail = await InventoryService.get_tier_availability(db, tier_id)
    if not avail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket tier not found.")
    return avail

