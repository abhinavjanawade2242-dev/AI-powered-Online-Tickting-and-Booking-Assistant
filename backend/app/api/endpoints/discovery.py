from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.models import Event, TicketTier, User
from app.services.event_service import EventService
from app.schemas import (
    EventResponse,
    EventDetailResponse,
    VenueResponse,
    TicketTierResponse,
    EventCreateRequest,
    EventUpdateRequest,
    TicketTierCreate,
)

router = APIRouter(prefix="/events", tags=["Stage 1 & 2: Discovery & Recommendation"])


@router.get("", response_model=List[EventResponse], summary="Discovery: Search events")
async def search_events(
    query: Optional[str] = Query(None, description="Keywords to match in event title, description or venue"),
    q: Optional[str] = Query(None, description="Alias for query"),
    search: Optional[str] = Query(None, description="Alias for query"),
    venue_id: Optional[str] = Query(None, description="Filter by venue ID"),
    city: Optional[str] = Query(None, description="Filter by venue city"),
    category: Optional[str] = Query(None, description="Filter by event category (Concert, Comedy, Sports, Theater)"),
    date_from: Optional[datetime] = Query(None, description="Start date filter"),
    date_to: Optional[datetime] = Query(None, description="End date filter"),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Stage 1: Discovery.
    Search upcoming events by keyword, location city, category, or date range.
    """
    effective_query = query or q or search
    events = await EventService.search_events(
        db=db,
        query=effective_query,
        city=city,
        category=category,
        venue_id=venue_id,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset
    )
    return events


@router.get("/recommendations", response_model=List[EventResponse], summary="Recommendation: Curated events")
async def get_recommended_events(
    category: Optional[str] = Query(None, description="Preferred category"),
    city: Optional[str] = Query(None, description="Preferred city"),
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """
    Stage 2: Recommendation.
    Assistant presents suitable venues, events, and curated choices.
    """
    events = await EventService.get_recommendations(
        db=db,
        category=category,
        city=city,
        limit=limit
    )
    return events


@router.get("/{event_id}", response_model=EventDetailResponse, summary="Get full event details")
async def get_event_detail(
    event_id: str,
    db: AsyncSession = Depends(get_db)
):
    event = await EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    min_price = min([float(t.price) for t in event.ticket_tiers]) if event.ticket_tiers else 0.0
    max_price = max([float(t.price) for t in event.ticket_tiers]) if event.ticket_tiers else 0.0
    total_avail = sum(t.available_quantity for t in event.ticket_tiers)

    return EventDetailResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        category=event.category,
        start_time=event.start_time,
        end_time=event.end_time,
        status=event.status,
        image_url=event.image_url,
        venue_id=event.venue_id,
        created_at=event.created_at,
        venue=VenueResponse.model_validate(event.venue) if event.venue else None,
        ticket_tiers=[TicketTierResponse.model_validate(t) for t in event.ticket_tiers],
        min_price=min_price,
        max_price=max_price,
        total_available_tickets=total_avail
    )


@router.post("", response_model=EventDetailResponse, status_code=status.HTTP_201_CREATED, summary="Create event (Admin/Organizer)")
async def create_event(
    req: EventCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "organizer"]))
):
    """
    Section 2.B: Create an event across campus venues.
    Requires 'admin' or 'organizer' role.
    """
    new_event = Event(
        venue_id=req.venue_id,
        title=req.title.strip(),
        description=req.description,
        category=req.category.strip(),
        start_time=req.start_time,
        end_time=req.end_time,
        image_url=req.image_url,
        status="ACTIVE"
    )
    db.add(new_event)
    await db.flush()

    for tier_data in req.ticket_tiers:
        tier = TicketTier(
            event_id=new_event.id,
            name=tier_data.name,
            price=tier_data.price,
            currency="INR",
            total_quantity=tier_data.total_quantity,
            available_quantity=tier_data.total_quantity
        )
        db.add(tier)

    await db.commit()
    refreshed = await EventService.get_event_by_id(db, new_event.id)
    min_price = min([float(t.price) for t in refreshed.ticket_tiers]) if refreshed.ticket_tiers else 0.0
    max_price = max([float(t.price) for t in refreshed.ticket_tiers]) if refreshed.ticket_tiers else 0.0
    total_avail = sum(t.available_quantity for t in refreshed.ticket_tiers)

    return EventDetailResponse(
        id=refreshed.id,
        title=refreshed.title,
        description=refreshed.description,
        category=refreshed.category,
        start_time=refreshed.start_time,
        end_time=refreshed.end_time,
        status=refreshed.status,
        image_url=refreshed.image_url,
        venue_id=refreshed.venue_id,
        created_at=refreshed.created_at,
        venue=VenueResponse.model_validate(refreshed.venue) if refreshed.venue else None,
        ticket_tiers=[TicketTierResponse.model_validate(t) for t in refreshed.ticket_tiers],
        min_price=min_price,
        max_price=max_price,
        total_available_tickets=total_avail
    )


@router.put("/{event_id}", response_model=EventDetailResponse, summary="Update event details (Admin/Organizer)")
async def update_event(
    event_id: str,
    req: EventUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "organizer"]))
):
    """
    Section 2.B: Update event metadata, schedule, or status.
    """
    event = await EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    if req.title is not None:
        event.title = req.title.strip()
    if req.description is not None:
        event.description = req.description
    if req.category is not None:
        event.category = req.category.strip()
    if req.start_time is not None:
        event.start_time = req.start_time
    if req.end_time is not None:
        event.end_time = req.end_time
    if req.status is not None:
        event.status = req.status.strip().upper()
    if req.image_url is not None:
        event.image_url = req.image_url

    await db.commit()
    refreshed = await EventService.get_event_by_id(db, event_id)
    min_price = min([float(t.price) for t in refreshed.ticket_tiers]) if refreshed.ticket_tiers else 0.0
    max_price = max([float(t.price) for t in refreshed.ticket_tiers]) if refreshed.ticket_tiers else 0.0
    total_avail = sum(t.available_quantity for t in refreshed.ticket_tiers)

    return EventDetailResponse(
        id=refreshed.id,
        title=refreshed.title,
        description=refreshed.description,
        category=refreshed.category,
        start_time=refreshed.start_time,
        end_time=refreshed.end_time,
        status=refreshed.status,
        image_url=refreshed.image_url,
        venue_id=refreshed.venue_id,
        created_at=refreshed.created_at,
        venue=VenueResponse.model_validate(refreshed.venue) if refreshed.venue else None,
        ticket_tiers=[TicketTierResponse.model_validate(t) for t in refreshed.ticket_tiers],
        min_price=min_price,
        max_price=max_price,
        total_available_tickets=total_avail
    )


@router.delete("/{event_id}", summary="Deactivate event (Admin/Organizer)")
async def deactivate_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "organizer"]))
):
    """
    Section 2.B: Deactivate an event (removes from public discovery).
    """
    event = await EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    event.status = "INACTIVE"
    await db.commit()
    return {"message": f"Event '{event.title}' successfully deactivated."}


venues_router = APIRouter(prefix="/venues", tags=["Stage 1 & 2: Venues"])


@venues_router.get("", response_model=List[VenueResponse], summary="Discovery: List venues")
async def list_venues(
    city: Optional[str] = Query(None, description="Filter by city"),
    query: Optional[str] = Query(None, description="Search venue name"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    return await EventService.search_venues(db=db, city=city, query=query, limit=limit)

