from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import TicketTier, Event
from app.schemas import TicketTierAvailability


class InventoryService:

    @staticmethod
    async def get_tier_availability(
        db: AsyncSession,
        tier_id: str
    ) -> Optional[TicketTierAvailability]:
        """
        Stage 3: Availability check for a single ticket tier.
        """
        stmt = select(TicketTier).where(TicketTier.id == tier_id)
        result = await db.execute(stmt)
        tier = result.scalar_one_or_none()
        if not tier:
            return None

        return TicketTierAvailability(
            tier_id=tier.id,
            name=tier.name,
            price=float(tier.price),
            currency=tier.currency,
            available_quantity=tier.available_quantity,
            is_sold_out=(tier.available_quantity <= 0)
        )

    @staticmethod
    async def get_event_inventory(
        db: AsyncSession,
        event_id: str
    ) -> Dict[str, Any]:
        """
        Stage 3: Comprehensive availability inspection for an event.
        Returns live seat quantities, pricing, and sold-out flags for each tier.
        """
        stmt = (
            select(Event)
            .options(selectinload(Event.ticket_tiers))
            .where(Event.id == event_id)
        )
        result = await db.execute(stmt)
        event = result.scalar_one_or_none()
        if not event:
            raise ValueError(f"Event with id {event_id} not found.")

        tiers_availability = [
            TicketTierAvailability(
                tier_id=t.id,
                name=t.name,
                price=float(t.price),
                currency=t.currency,
                available_quantity=t.available_quantity,
                is_sold_out=(t.available_quantity <= 0)
            )
            for t in event.ticket_tiers
        ]

        total_available = sum(t.available_quantity for t in event.ticket_tiers)
        min_price = min([float(t.price) for t in event.ticket_tiers]) if event.ticket_tiers else 0.0
        max_price = max([float(t.price) for t in event.ticket_tiers]) if event.ticket_tiers else 0.0

        return {
            "event_id": event.id,
            "title": event.title,
            "category": event.category,
            "start_time": event.start_time,
            "total_available_tickets": total_available,
            "min_price": min_price,
            "max_price": max_price,
            "tiers": tiers_availability,
            "is_sold_out": (total_available <= 0)
        }

