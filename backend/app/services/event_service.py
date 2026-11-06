from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import select, or_, and_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Event, Venue, TicketTier


class EventService:

    @staticmethod
    async def search_events(
        db: AsyncSession,
        query: Optional[str] = None,
        city: Optional[str] = None,
        category: Optional[str] = None,
        venue_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Event]:
        """
        Stage 1: Discovery.
        Find events matching text search, venue location, category, or date range.
        """
        stmt = (
            select(Event)
            .join(Event.venue)
            .options(
                selectinload(Event.venue),
                selectinload(Event.ticket_tiers)
            )
            .where(Event.status == "ACTIVE")
        )

        filters = []
        if query:
            q_pattern = f"%{query.strip()}%"
            filters.append(
                or_(
                    Event.title.ilike(q_pattern),
                    Event.description.ilike(q_pattern),
                    Venue.name.ilike(q_pattern),
                )
            )

        if venue_id:
            filters.append(Event.venue_id == venue_id.strip())

        if city:
            filters.append(Venue.city.ilike(f"%{city.strip()}%"))

        if category:
            filters.append(Event.category.ilike(f"%{category.strip()}%"))

        if date_from:
            filters.append(Event.start_time >= date_from)

        if date_to:
            filters.append(Event.start_time <= date_to)

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.order_by(Event.start_time.asc()).limit(limit).offset(offset)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_recommendations(
        db: AsyncSession,
        category: Optional[str] = None,
        city: Optional[str] = None,
        limit: int = 5
    ) -> List[Event]:
        """
        Stage 2: Recommendation.
        Returns top-tier recommended events based on popularity, category, or proximity.
        """
        stmt = (
            select(Event)
            .join(Event.venue)
            .options(
                selectinload(Event.venue),
                selectinload(Event.ticket_tiers)
            )
            .where(Event.status == "ACTIVE")
        )

        conditions = []
        if category:
            conditions.append(Event.category.ilike(f"%{category.strip()}%"))
        if city:
            conditions.append(Venue.city.ilike(f"%{city.strip()}%"))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Recommend upcoming events
        stmt = stmt.where(Event.start_time >= datetime.utcnow()).order_by(Event.start_time.asc()).limit(limit)
        result = await db.execute(stmt)
        events = list(result.scalars().all())

        # If no strict match, fallback to general upcoming events
        if not events:
            fallback_stmt = (
                select(Event)
                .options(selectinload(Event.venue), selectinload(Event.ticket_tiers))
                .where(Event.status == "ACTIVE")
                .order_by(Event.start_time.asc())
                .limit(limit)
            )
            fallback_res = await db.execute(fallback_stmt)
            events = list(fallback_res.scalars().all())

        return events

    @staticmethod
    async def get_event_by_id(db: AsyncSession, event_id: str) -> Optional[Event]:
        stmt = (
            select(Event)
            .options(
                selectinload(Event.venue),
                selectinload(Event.ticket_tiers)
            )
            .where(Event.id == event_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def search_venues(
        db: AsyncSession,
        city: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 10
    ) -> List[Venue]:
        stmt = select(Venue)
        filters = []
        if city:
            filters.append(Venue.city.ilike(f"%{city.strip()}%"))
        if query:
            filters.append(Venue.name.ilike(f"%{query.strip()}%"))
        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.order_by(Venue.name.asc()).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

