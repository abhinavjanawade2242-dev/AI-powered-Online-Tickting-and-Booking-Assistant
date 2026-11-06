import json
import logging
import re
import uuid
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import ChatSession, ChatMessage, Event, TicketTier
from app.schemas import ChatResponse, ChatActionSuggestion
from app.ai.prompts import TICKETING_ASSISTANT_SYSTEM_PROMPT
from app.ai.tools import AgentTools

logger = logging.getLogger("ticketing.ai.agent")

# Journey stages defined in product specification
STAGES = [
    "Discovery",
    "Recommendation",
    "Availability",
    "Selection",
    "Booking",
    "Confirmation",
    "Post-booking"
]


class ConversationalTicketingAgent:
    """
    Intelligent Conversational Agent coordinating the 7-Stage Customer Booking Journey.
    Supports OpenAI, Google Gemini, and a zero-dependency deterministic engine for offline testing.
    """

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.openai_key = settings.OPENAI_API_KEY
        self.gemini_key = settings.GEMINI_API_KEY

    async def get_or_create_session(
        self,
        db: AsyncSession,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> ChatSession:
        if not session_id:
            session_id = f"sess_{uuid.uuid4().hex[:12]}"

        stmt = (
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(ChatSession.id == session_id)
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            session = ChatSession(
                id=session_id,
                user_id=user_id,
                current_stage="Discovery",
                context_data="{}"
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)

        return session

    async def process_message(
        self,
        db: AsyncSession,
        user_message: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> ChatResponse:
        session = await self.get_or_create_session(db, session_id, user_id)
        context = json.loads(session.context_data or "{}")

        # Record incoming user message
        user_msg_record = ChatMessage(
            session_id=session.id,
            role="user",
            content=user_message
        )
        db.add(user_msg_record)
        await db.commit()

        # Decide processing mode: LLM API vs Built-in Intent Engine
        if self.provider == "openai" and self.openai_key:
            response_text, stage, updated_context, suggestions, tool_calls = await self._run_openai_agent(
                db, session, user_message, context
            )
        elif self.provider == "gemini" and self.gemini_key:
            response_text, stage, updated_context, suggestions, tool_calls = await self._run_gemini_agent(
                db, session, user_message, context
            )
        else:
            # Deterministic, high-fidelity Intent & Tool Execution Engine
            response_text, stage, updated_context, suggestions, tool_calls = await self._run_intent_engine(
                db, user_message, session.current_stage, context
            )

        # Update persistent session state
        session.current_stage = stage
        session.context_data = json.dumps(updated_context)
        ai_msg_record = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=response_text,
            tool_calls=json.dumps(tool_calls) if tool_calls else None
        )
        db.add(ai_msg_record)
        await db.commit()

        return ChatResponse(
            session_id=session.id,
            message=response_text,
            current_stage=stage,
            context_data=updated_context,
            suggested_actions=suggestions,
            tool_calls_executed=tool_calls
        )

    # --------------------------------------------------------------------------
    # Built-in Deterministic Intent & Stage Engine (Zero external dependencies)
    # --------------------------------------------------------------------------
    async def _run_intent_engine(
        self,
        db: AsyncSession,
        text: str,
        current_stage: str,
        context: Dict[str, Any]
    ) -> Tuple[str, str, Dict[str, Any], List[ChatActionSuggestion], List[str]]:
        lower = text.lower()
        tool_calls: List[str] = []
        suggestions: List[ChatActionSuggestion] = []

        # ----------------------------------------------------------------------
        # STAGE 7 Check: Booking status inquiry or cancellation
        # ----------------------------------------------------------------------
        bk_match = re.search(r"\b(BK-[A-Z0-9]{6})\b", text, re.IGNORECASE)
        if "cancel" in lower and bk_match:
            ref = bk_match.group(1).upper()
            tool_calls.append(f"cancel_booking('{ref}')")
            res = await AgentTools.cancel_booking(db, ref)
            stage = "Post-booking"
            if res.get("success"):
                reply = (
                    f"✅ **Booking Cancelled Successfully**\n\n"
                    f"Your booking **{ref}** has been cancelled. "
                    f"{res.get('quantity_released')} ticket(s) have been safely returned to inventory."
                )
            else:
                reply = f"❌ Could not cancel booking: {res.get('message')}"
            return reply, stage, context, suggestions, tool_calls

        if bk_match or "status" in lower or "my ticket" in lower or "check booking" in lower:
            ref = bk_match.group(1).upper() if bk_match else context.get("last_booking_ref")
            if ref:
                tool_calls.append(f"get_booking_details('{ref}')")
                res = await AgentTools.get_booking_details(db, ref)
                stage = "Post-booking"
                if res.get("found"):
                    tickets_info = "\n".join(
                        [f"- Ticket Code: `{t['ticket_code']}` | Seat: {t['seat_number']} | Status: **{t['status']}**" for t in res.get("tickets", [])]
                    )
                    reply = (
                        f"🎟️ **Booking Details for {ref}**\n\n"
                        f"- **Event**: {res['event_title']}\n"
                        f"- **Date & Time**: {res['start_time']}\n"
                        f"- **Venue**: {res['venue_name']}\n"
                        f"- **Tier**: {res['tier_name']} (Quantity: {res['quantity']})\n"
                        f"- **Total Paid**: {res['total_amount']}\n"
                        f"- **Status**: **{res['status']}**\n\n"
                        f"**Your Digital Tickets:**\n{tickets_info}\n\n"
                        f"Present your digital QR code at gate entrance for scan verification."
                    )
                    suggestions.append(ChatActionSuggestion(label="Cancel Booking", action_type="cancel_booking", payload={"ref": ref}))
                else:
                    reply = f"🔍 {res.get('message')}"
                return reply, stage, context, suggestions, tool_calls

        # ----------------------------------------------------------------------
        # STAGE 4 & 5 Check: Selection & Booking Request
        # ----------------------------------------------------------------------
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        qty_match = re.search(r"\b([1-9]|10)\s*(tickets?|seats?|tix)?\b", lower)

        if ("book" in lower or "reserve" in lower or "buy" in lower or email_match) and (context.get("selected_event_id") or "event" in lower):
            event_id = context.get("selected_event_id")
            tier_id = context.get("selected_tier_id")
            quantity = int(qty_match.group(1)) if qty_match else context.get("selected_quantity", 1)

            # Check if user provided email or tier
            if not email_match:
                stage = "Selection"
                # Ask for user details
                reply = (
                    f"Great! I have reserved **{quantity} ticket(s)** for you.\n\n"
                    f"To finalize your booking, please provide your **Full Name and Email Address** "
                    f"(e.g., *'Book for Alex Smith, alex@example.com'*)."
                )
                context["selected_quantity"] = quantity
                return reply, stage, context, suggestions, tool_calls

            # Email was provided! Extract name and process booking
            customer_email = email_match.group(0)
            customer_name = text.split(",")[0].replace("book for", "").replace("Book for", "").strip()
            if customer_email in customer_name:
                customer_name = "Guest Customer"

            # If no tier selected, default to first available tier
            if not tier_id and event_id:
                inv = await AgentTools.check_ticket_availability(db, event_id)
                for t in inv.get("tiers", []):
                    if t.get("available_quantity", 0) >= quantity:
                        tier_id = t.get("tier_id")
                        context["selected_tier_id"] = tier_id
                        break

            if event_id and tier_id:
                tool_calls.append(f"reserve_and_book_tickets(event='{event_id}', tier='{tier_id}', qty={quantity})")
                res = await AgentTools.reserve_and_book_tickets(
                    db=db,
                    event_id=event_id,
                    tier_id=tier_id,
                    quantity=quantity,
                    customer_name=customer_name or "Guest Customer",
                    customer_email=customer_email
                )

                if res.get("success"):
                    stage = "Confirmation"
                    ref = res["booking_reference"]
                    context["last_booking_ref"] = ref
                    tickets_summary = "\n".join(
                        [f"- Ticket `{t['ticket_code']}` ({t['seat_number']})" for t in res.get("tickets", [])]
                    )
                    reply = (
                        f"🎉 **Booking Confirmed!** (Stage 6: Confirmation)\n\n"
                        f"Your booking reference: **{ref}**\n"
                        f"- **Event**: {context.get('selected_event_title', 'Confirmed Event')}\n"
                        f"- **Tier**: {res.get('tier_name')}\n"
                        f"- **Quantity**: {res.get('quantity')}\n"
                        f"- **Total**: {res.get('total_amount')}\n"
                        f"- **Customer**: {customer_name} ({customer_email})\n\n"
                        f"**Digital Tickets Generated:**\n{tickets_summary}\n\n"
                        f"A digital confirmation token with gate QR check-in has been issued. "
                        f"You can retrieve or manage this order anytime using reference `{ref}`."
                    )
                    suggestions.append(ChatActionSuggestion(label="View Ticket Status", action_type="view_booking", payload={"ref": ref}))
                    suggestions.append(ChatActionSuggestion(label="Find More Events", action_type="discovery", payload={}))
                    return reply, stage, context, suggestions, tool_calls
                else:
                    reply = f"⚠️ Could not complete booking: {res.get('message')}"
                    stage = "Selection"
                    return reply, stage, context, suggestions, tool_calls

        # ----------------------------------------------------------------------
        # STAGE 3 Check: Availability inquiry
        # ----------------------------------------------------------------------
        if ("availability" in lower or "tickets left" in lower or "how many" in lower or "price" in lower) and context.get("selected_event_id"):
            event_id = context.get("selected_event_id")
            tool_calls.append(f"check_ticket_availability('{event_id}')")
            inv = await AgentTools.check_ticket_availability(db, event_id)
            stage = "Availability"

            tiers_md = "\n".join(
                [f"- **{t['tier_name']}**: {t['price']} ({t['status']}) - `ID: {t['tier_id']}`" for t in inv.get("tiers", [])]
            )
            reply = (
                f"🎫 **Live Ticket Inventory for {inv.get('event_title', 'Event')}** (Stage 3: Availability)\n\n"
                f"{tiers_md}\n\n"
                f"**Total Available Tickets**: {inv.get('total_available_tickets')}\n\n"
                f"Which ticket tier and quantity would you like to select? (e.g., *'Book 2 VIP tickets'*)"
            )
            for t in inv.get("tiers", []):
                suggestions.append(ChatActionSuggestion(
                    label=f"Select {t['tier_name']} ({t['price']})",
                    action_type="select_tier",
                    payload={"tier_id": t["tier_id"], "tier_name": t["tier_name"]}
                ))
            return reply, stage, context, suggestions, tool_calls

        # ----------------------------------------------------------------------
        # STAGE 1 & 2: Discovery & Recommendation
        # ----------------------------------------------------------------------
        tool_calls.append(f"search_events_and_venues(text='{text}')")
        city_candidate = None
        for c in ["New York", "Chicago", "San Francisco", "Austin", "London", "Los Angeles"]:
            if c.lower() in lower:
                city_candidate = c
                break

        category_candidate = None
        for cat in ["Concert", "Comedy", "Sports", "Theater", "Festival"]:
            if cat.lower() in lower:
                category_candidate = cat
                break

        res = await AgentTools.search_events_and_venues(
            db,
            query=None if (city_candidate or category_candidate) else text,
            city=city_candidate,
            category=category_candidate
        )

        events = res.get("events", [])
        if events:
            stage = "Recommendation"
            top_event = events[0]
            context["selected_event_id"] = top_event["event_id"]
            context["selected_event_title"] = top_event["title"]

            events_md = ""
            for idx, e in enumerate(events[:3], 1):
                events_md += (
                    f"{idx}. **{e['title']}**\n"
                    f"   - 📍 Venue: {e['venue_name']} ({e['city']})\n"
                    f"   - 🗓️ Date: {e['start_time']}\n"
                    f"   - 💵 From: {e['starting_price']}\n"
                    f"   - 🏷️ Category: {e['category']}\n\n"
                )

            reply = (
                f"👋 **Here are the top recommended events matching your request:** (Stage 2: Recommendation)\n\n"
                f"{events_md}"
                f"Would you like to check **real-time ticket availability and pricing** for any of these?"
            )
            for e in events[:3]:
                suggestions.append(ChatActionSuggestion(
                    label=f"Check '{e['title'][:25]}...'",
                    action_type="check_availability",
                    payload={"event_id": e["event_id"]}
                ))
        else:
            stage = "Discovery"
            reply = (
                "👋 Welcome to the AI Ticketing & Booking Assistant!\n\n"
                "I can help you discover exciting concerts, comedy shows, sports events, and theater. "
                "What city or type of event are you looking for?"
            )
            suggestions.append(ChatActionSuggestion(label="Concerts in New York", action_type="search", payload={"city": "New York", "category": "Concert"}))
            suggestions.append(ChatActionSuggestion(label="Comedy in Chicago", action_type="search", payload={"city": "Chicago", "category": "Comedy"}))

        return reply, stage, context, suggestions, tool_calls

    # --------------------------------------------------------------------------
    # LangChain / OpenAI Provider Integration
    # --------------------------------------------------------------------------
    async def _run_openai_agent(
        self,
        db: AsyncSession,
        session: ChatSession,
        user_message: str,
        context: Dict[str, Any]
    ) -> Tuple[str, str, Dict[str, Any], List[ChatActionSuggestion], List[str]]:
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

            llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.2
            )
            # Retrieve recent conversation messages
            messages = [SystemMessage(content=TICKETING_ASSISTANT_SYSTEM_PROMPT)]
            for m in session.messages[-5:]:
                if m.role == "user":
                    messages.append(HumanMessage(content=m.content))
                elif m.role == "assistant":
                    messages.append(AIMessage(content=m.content))

            messages.append(HumanMessage(content=user_message))
            ai_msg = await llm.ainvoke(messages)
            reply = ai_msg.content
            return reply, session.current_stage, context, [], ["openai_llm_invocation"]
        except Exception as e:
            logger.error("OpenAI invocation failed: %s. Falling back to intent engine.", e)
            return await self._run_intent_engine(db, user_message, session.current_stage, context)

    # --------------------------------------------------------------------------
    # Google Gemini Provider Integration
    # --------------------------------------------------------------------------
    async def _run_gemini_agent(
        self,
        db: AsyncSession,
        session: ChatSession,
        user_message: str,
        context: Dict[str, Any]
    ) -> Tuple[str, str, Dict[str, Any], List[ChatActionSuggestion], List[str]]:
        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                system_instruction=TICKETING_ASSISTANT_SYSTEM_PROMPT
            )
            chat = model.start_chat()
            res = chat.send_message(user_message)
            return res.text, session.current_stage, context, [], ["gemini_llm_invocation"]
        except Exception as e:
            logger.error("Gemini invocation failed: %s. Falling back to intent engine.", e)
            return await self._run_intent_engine(db, user_message, session.current_stage, context)


agent_instance = ConversationalTicketingAgent()

