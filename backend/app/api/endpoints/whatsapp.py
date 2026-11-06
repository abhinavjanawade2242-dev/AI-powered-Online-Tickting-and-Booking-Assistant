import logging
from typing import Optional
from fastapi import APIRouter, Depends, Header, Query, Request, Response, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.services.whatsapp_service import WhatsAppService
from app.schemas import WhatsAppSimulateRequest, WhatsAppSimulateResponse

logger = logging.getLogger("ticketing.whatsapp.api")
router = APIRouter(prefix="/whatsapp", tags=["Section H: WhatsApp Integration Channel"])


@router.get("/webhook", summary="Meta WhatsApp Webhook Verification Challenge")
async def verify_whatsapp_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
):
    """
    Section 2.H: Meta WhatsApp Cloud API Webhook Verification.
    Meta sends a GET request with hub.mode, hub.verify_token, and hub.challenge.
    Must return hub.challenge with HTTP 200 when verify_token matches.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp webhook challenge verified successfully.")
        return PlainTextResponse(content=hub_challenge or "", status_code=200)

    logger.warning("WhatsApp webhook challenge failed: token mismatch or invalid mode.")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification token mismatch.")


@router.post("/webhook", summary="Receive Meta WhatsApp Cloud API Webhook Events")
async def receive_whatsapp_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256")
):
    """
    Section 2.H: Receive and process incoming WhatsApp messages.
    - Validates HMAC-SHA256 signature against app secret.
    - Deduplicates incoming message IDs.
    - Maps sender phone to stable chat session (wa_{phone}).
    - Forwards to existing AI Conversational Agent.
    """
    raw_body = await request.body()
    if not WhatsAppService.verify_webhook_signature(raw_body, x_hub_signature_256):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid webhook signature."
        )

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload.")

    messages = WhatsAppService.extract_messages_from_webhook(payload)
    for msg in messages:
        await WhatsAppService.process_whatsapp_message(
            db=db,
            sender_phone=msg["sender_phone"],
            message_text=msg["text"],
            message_id=msg["message_id"]
        )

    return {"status": "EVENT_RECEIVED"}


@router.post("/simulate", response_model=WhatsAppSimulateResponse, summary="Simulate WhatsApp Message (QA & Local Test)")
async def simulate_whatsapp_message(
    req: WhatsAppSimulateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Section 2.H: Developer & QA Simulator.
    Simulates receiving an inbound WhatsApp message from a phone number,
    routing it through the existing AI agent, and generating the outbound reply.
    """
    result = await WhatsAppService.process_whatsapp_message(
        db=db,
        sender_phone=req.sender_phone,
        message_text=req.message
    )

    return WhatsAppSimulateResponse(
        sender_phone=req.sender_phone,
        session_id=result["session_id"],
        incoming_message=req.message,
        assistant_reply=result["reply"] or "",
        current_stage=result["stage"],
        language=result["language"],
        delivered=True,
        delivery_channel="Meta WhatsApp Cloud API (Simulated)"
    )
