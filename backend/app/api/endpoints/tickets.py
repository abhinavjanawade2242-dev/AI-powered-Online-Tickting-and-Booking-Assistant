from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.models import DigitalTicket
from app.services.ticket_service import TicketService
from app.schemas import DigitalTicketResponse

router = APIRouter(prefix="/tickets", tags=["Stage 6 & 7: Digital Tickets & Gate Check-in"])


class TicketVerifyRequest(BaseModel):
    qr_payload: str


class TicketVerifyResponse(BaseModel):
    is_valid: bool
    ticket_code: str
    status: str
    message: str


@router.get("/{ticket_code}", response_model=DigitalTicketResponse, summary="Get Digital Ticket info")
async def get_ticket(
    ticket_code: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(DigitalTicket)
        .options(selectinload(DigitalTicket.ticket_tier))
        .where(DigitalTicket.ticket_code == ticket_code.strip().upper())
    )
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found.")

    return DigitalTicketResponse(
        id=ticket.id,
        ticket_code=ticket.ticket_code,
        tier_id=ticket.tier_id,
        tier_name=ticket.ticket_tier.name if ticket.ticket_tier else None,
        qr_payload=ticket.qr_payload,
        status=ticket.status,
        issued_at=ticket.issued_at
    )


@router.get("/{ticket_code}/qr", summary="Get Base64 PNG QR Code image for ticket")
async def get_ticket_qr_image(
    ticket_code: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(DigitalTicket).where(DigitalTicket.ticket_code == ticket_code.strip().upper())
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found.")

    b64_img = TicketService.create_qr_code_base64(ticket.qr_payload)
    return {
        "ticket_code": ticket.ticket_code,
        "qr_base64": b64_img,
        "format": "image/png"
    }


@router.post("/verify", response_model=TicketVerifyResponse, summary="Gate Entrance Scan Verification")
async def verify_ticket_qr(
    req: TicketVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Gate check-in scanner verification.
    Validates QR signature and checks if the ticket is ACTIVE.
    """
    is_signature_valid = TicketService.verify_qr_payload(req.qr_payload)
    if not is_signature_valid:
        return TicketVerifyResponse(
            is_valid=False,
            ticket_code="UNKNOWN",
            status="INVALID_SIGNATURE",
            message="Tampered or invalid ticket QR code."
        )

    parts = req.qr_payload.split("|")
    ticket_code = parts[0]

    stmt = select(DigitalTicket).where(DigitalTicket.ticket_code == ticket_code)
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()

    if not ticket:
        return TicketVerifyResponse(
            is_valid=False,
            ticket_code=ticket_code,
            status="NOT_FOUND",
            message="Ticket record does not exist in the database."
        )

    if ticket.status == "USED":
        return TicketVerifyResponse(
            is_valid=False,
            ticket_code=ticket_code,
            status="ALREADY_USED",
            seat_number=ticket.seat_number,
            message="Ticket has already been scanned and checked in."
        )

    if ticket.status == "CANCELLED":
        return TicketVerifyResponse(
            is_valid=False,
            ticket_code=ticket_code,
            status="CANCELLED",
            seat_number=ticket.seat_number,
            message="Ticket was cancelled."
        )

    # Valid check-in: mark ticket as USED
    ticket.status = "USED"
    await db.commit()

    return TicketVerifyResponse(
        is_valid=True,
        ticket_code=ticket.ticket_code,
        status="USED",
        seat_number=ticket.seat_number,
        message="Valid ticket. Access granted!"
    )

