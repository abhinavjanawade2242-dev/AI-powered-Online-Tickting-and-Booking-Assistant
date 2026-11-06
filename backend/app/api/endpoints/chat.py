from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.models import ChatSession
from app.schemas import ChatRequest, ChatResponse
from app.ai.agent import agent_instance

router = APIRouter(prefix="/chat", tags=["AI Conversational Assistant (Workflow 1-7)"])


class MessageHistoryItem(BaseModel):
    role: str
    content: str
    created_at: str


class SessionHistoryResponse(BaseModel):
    session_id: str
    current_stage: str
    messages: List[MessageHistoryItem]


@router.post("", response_model=ChatResponse, summary="Send message to AI Ticketing Assistant")
async def chat_with_assistant(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Core Conversational Endpoint for the 7-Stage Customer Booking Workflow:
    1. Discovery: Search events & venues
    2. Recommendation: Get curated event suggestions
    3. Availability: Check live ticket tiers & pricing
    4. Selection: Guide ticket type and quantity
    5. Booking: Validate details & atomically lock inventory
    6. Confirmation: Record order & issue digital tickets
    7. Post-booking: Retrieve tickets & process cancellations
    """
    try:
        response = await agent_instance.process_message(
            db=db,
            user_message=req.message,
            session_id=req.session_id,
            user_id=req.user_id,
            preferred_language=getattr(req, "language", "en")
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Agent encountered an error: {str(e)}"
        )


@router.get("/history/{session_id}", response_model=SessionHistoryResponse, summary="Retrieve conversation history")
async def get_session_history(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == session_id)
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    items = [
        MessageHistoryItem(
            role=m.role,
            content=m.content,
            created_at=m.created_at.isoformat()
        )
        for m in session.messages
    ]

    return SessionHistoryResponse(
        session_id=session.id,
        current_stage=session.current_stage,
        messages=items
    )

