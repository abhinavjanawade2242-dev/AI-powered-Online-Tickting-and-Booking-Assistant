import json
import logging
import re
import uuid
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import ChatSession, ChatMessage
from app.schemas import ChatResponse, ChatActionSuggestion
from app.ai.prompts import TICKETING_ASSISTANT_SYSTEM_PROMPT
from app.ai.tools import AgentTools
from app.services.pricing_service import PricingService
from app.services.business_rules import BusinessRulesEngine

logger = logging.getLogger("ticketing.ai.agent")

STAGES = [
    "Discovery",
    "Recommendation",
    "Availability",
    "Selection",
    "Booking",
    "Confirmation",
    "Post-booking"
]


def detect_language(text: str, default_lang: Optional[str] = "en") -> str:
    """
    Detects user language:
    - 'kn': Kannada (script or romanized keywords)
    - 'hi': Hindi (Devanagari script or romanized keywords)
    - 'en': English (default)
    """
    if not text:
        return default_lang or "en"

    # Kannada Unicode Block: \u0C80 - \u0CFF
    if re.search(r"[\u0C80-\u0CFF]", text):
        return "kn"

    # Devanagari / Hindi Unicode Block: \u0900 - \u097F
    if re.search(r"[\u0900-\u097F]", text):
        return "hi"

    lower = text.lower()
    kannada_keywords = ["kannada", "namaskara", "namaskar", "hegiddira", "dhanyavada", "beku", "tumba", "yavaga", "eshtu"]
    if any(k in lower for k in kannada_keywords):
        return "kn"

    hindi_keywords = ["hindi", "namaste", "dhanyawad", "shukriya", "kripya", "chahiye", "kitne", "karein", "kaise", "hoga"]
    if any(k in lower for k in hindi_keywords):
        return "hi"

    return default_lang or "en"


class ConversationalTicketingAgent:
    """
    Intelligent Conversational Agent coordinating the 7-Stage Customer Booking Journey.
    Supports English, Kannada, and Hindi.
    Integrates Pricing Engine, Anti-Overbooking Concurrency, and General Admission rules.
    """

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.openai_key = settings.OPENAI_API_KEY
        self.gemini_key = settings.GEMINI_API_KEY

    async def get_or_create_session(
        self,
        db: AsyncSession,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        preferred_language: Optional[str] = "en"
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
                context_data=json.dumps({"language": preferred_language or "en"})
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
        user_id: Optional[str] = None,
        preferred_language: Optional[str] = "en"
    ) -> ChatResponse:
        session = await self.get_or_create_session(db, session_id, user_id, preferred_language)
        context = json.loads(session.context_data or "{}")

        # Determine effective language
        detected_lang = detect_language(user_message, default_lang=preferred_language or context.get("language", "en"))
        context["language"] = detected_lang

        # Record incoming user message
        user_msg_record = ChatMessage(
            session_id=session.id,
            role="user",
            content=user_message
        )
        db.add(user_msg_record)
        await db.commit()

        # Decide processing mode
        if self.provider == "openai" and self.openai_key:
            response_text, stage, updated_context, suggestions, tool_calls = await self._run_openai_agent(
                db, session, user_message, context, detected_lang
            )
        elif self.provider == "gemini" and self.gemini_key:
            response_text, stage, updated_context, suggestions, tool_calls = await self._run_gemini_agent(
                db, session, user_message, context, detected_lang
            )
        else:
            # Deterministic, high-fidelity Multilingual Intent & Tool Execution Engine
            response_text, stage, updated_context, suggestions, tool_calls = await self._run_intent_engine(
                db, user_message, session.current_stage, context, detected_lang
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
            language=detected_lang,
            context_data=updated_context,
            suggested_actions=suggestions,
            tool_calls_executed=tool_calls
        )

    # --------------------------------------------------------------------------
    # Built-in Multilingual Intent & Tool Execution Engine
    # --------------------------------------------------------------------------
    async def _run_intent_engine(
        self,
        db: AsyncSession,
        text: str,
        current_stage: str,
        context: Dict[str, Any],
        lang: str = "en"
    ) -> Tuple[str, str, Dict[str, Any], List[ChatActionSuggestion], List[str]]:
        lower = text.lower()
        tool_calls: List[str] = []
        suggestions: List[ChatActionSuggestion] = []

        # ----------------------------------------------------------------------
        # STAGE 7: Booking status inquiry or cancellation
        # ----------------------------------------------------------------------
        bk_match = re.search(r"\b(BK-[A-Z0-9]{6})\b", text, re.IGNORECASE)
        is_cancel = any(k in lower for k in ["cancel", "ರದ್ದು", "रद्द"])

        if is_cancel and bk_match:
            ref = bk_match.group(1).upper()
            tool_calls.append(f"cancel_booking('{ref}')")
            res = await AgentTools.cancel_booking(db, ref)
            stage = "Post-booking"

            if res.get("success"):
                if lang == "kn":
                    reply = (
                        f"✅ **ಬುಕಿಂಗ್ ಯಶಸ್ವಿಯಾಗಿ ರದ್ದುಗೊಂಡಿದೆ (Booking Cancelled Successfully)**\n\n"
                        f"ನಿಮ್ಮ ಬುಕಿಂಗ್ ಸಂಖ್ಯೆ **{ref}** ಅನ್ನು ರದ್ದುಗೊಳಿಸಲಾಗಿದೆ.\n"
                        f"- ಮರುಪಾವತಿ ಮೊತ್ತ: **{res.get('refund_amount')}** ({res.get('refund_status')})\n"
                        f"- {res.get('quantity_released')} ಟಿಕೆಟ್(ಗಳು) ದಾಸ್ತಾನು ಸಂಗ್ರಹಕ್ಕೆ ಮರಳಿಸಲಾಗಿದೆ."
                    )
                elif lang == "hi":
                    reply = (
                        f"✅ **बुकिंग सफलतापूर्वक रद्द कर दी गई है (Booking Cancelled Successfully)**\n\n"
                        f"आपकी बुकिंग संदर्भ संख्या **{ref}** रद्द कर दी गई है।\n"
                        f"- रिफंड राशि: **{res.get('refund_amount')}** ({res.get('refund_status')})\n"
                        f"- {res.get('quantity_released')} टिकट पुनः इन्वेंट्री में जोड़ दिए गए हैं।"
                    )
                else:
                    reply = (
                        f"✅ **Booking Cancelled Successfully**\n\n"
                        f"Your booking **{ref}** has been cancelled.\n"
                        f"- 100% Refund: **{res.get('refund_amount')}** ({res.get('refund_status')})\n"
                        f"- {res.get('quantity_released')} ticket(s) safely restored to inventory."
                    )
            else:
                if lang == "kn":
                    reply = f"❌ ಬುಕಿಂಗ್ ರದ್ದು ಮಾಡಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ: {res.get('message')}"
                elif lang == "hi":
                    reply = f"❌ बुकिंग रद्द करने में असमर्थ: {res.get('message')}"
                else:
                    reply = f"❌ Could not cancel booking: {res.get('message')}"
            return reply, stage, context, suggestions, tool_calls

        is_status_inquiry = (
            bk_match or
            any(k in lower for k in ["status", "my ticket", "check booking", "ಸ್ಥಿತಿ", "ನನ್ನ ಟಿಕೆಟ್", "स्थिति", "मेरा टिकट"])
        )
        if is_status_inquiry:
            ref = bk_match.group(1).upper() if bk_match else context.get("last_booking_ref")
            if ref:
                tool_calls.append(f"get_booking_details('{ref}')")
                res = await AgentTools.get_booking_details(db, ref)
                stage = "Post-booking"
                if res.get("found"):
                    tickets_info = "\n".join(
                        [f"- Ticket Code: `{t['ticket_code']}` | General Admission | Status: **{t['status']}**" for t in res.get("tickets", [])]
                    )
                    if lang == "kn":
                        reply = (
                            f"🎟️ **ಬುಕಿಂಗ್ ವಿವರಗಳು: {ref}** (Stage 7: Post-booking)\n\n"
                            f"- **ಕಾರ್ಯಕ್ರಮ (Event)**: {res['event_title']}\n"
                            f"- **ದಿನಾಂಕ & ಸಮಯ**: {res['start_time']}\n"
                            f"- **ಸ್ಥಳ (Venue)**: {res['venue_name']}\n"
                            f"- **ಟಿಕೆಟ್ ವರ್ಗ**: {res['tier_name']} (ಪ್ರಮಾಣ: {res['quantity']})\n"
                            f"- **ಪಾವತಿಸಿದ ಒಟ್ಟು ಮೊತ್ತ**: {res['total_amount']}\n"
                            f"- **ಸ್ಥಿತಿ (Status)**: **{res['status']}**\n\n"
                            f"**ನಿಮ್ಮ ಡಿಜಿಟಲ್ ಟಿಕೆಟ್‌ಗಳು (ಸಾಮಾನ್ಯ ಪ್ರವೇಶ - General Admission):**\n{tickets_info}\n\n"
                            f"ಪ್ರವೇಶ ದ್ವಾರದಲ್ಲಿ ಸ್ಕ್ಯಾನ್ ಮಾಡಲು ಡಿಜಿಟಲ್ ಕ್ಯೂಆರ್ ಕೋಡ್ ಪ್ರಸ್ತುತಪಡಿಸಿ."
                        )
                        suggestions.append(ChatActionSuggestion(label="ಬುಕಿಂಗ್ ರದ್ದು ಮಾಡಿ (Cancel)", action_type="cancel_booking", payload={"ref": ref}))
                    elif lang == "hi":
                        reply = (
                            f"🎟️ **बुकिंग विवरण: {ref}** (Stage 7: Post-booking)\n\n"
                            f"- **कार्यक्रम (Event)**: {res['event_title']}\n"
                            f"- **दिनांक और समय**: {res['start_time']}\n"
                            f"- **स्थान (Venue)**: {res['venue_name']}\n"
                            f"- **टिकट श्रेणी**: {res['tier_name']} (संख्या: {res['quantity']})\n"
                            f"- **कुल भुगतान**: {res['total_amount']}\n"
                            f"- **स्थिति (Status)**: **{res['status']}**\n\n"
                            f"**आपके डिजिटल टिकट (सामान्य प्रवेश - General Admission):**\n{tickets_info}\n\n"
                            f"प्रवेश द्वार पर सत्यापन के लिए डिजिटल क्यूआर कोड प्रस्तुत करें।"
                        )
                        suggestions.append(ChatActionSuggestion(label="बुकिंग रद्द करें (Cancel)", action_type="cancel_booking", payload={"ref": ref}))
                    else:
                        reply = (
                            f"🎟️ **Booking Details for {ref}** (Stage 7: Post-booking)\n\n"
                            f"- **Event**: {res['event_title']}\n"
                            f"- **Date & Time**: {res['start_time']}\n"
                            f"- **Venue**: {res['venue_name']}\n"
                            f"- **Tier**: {res['tier_name']} (Quantity: {res['quantity']})\n"
                            f"- **Total Paid**: {res['total_amount']}\n"
                            f"- **Status**: **{res['status']}**\n\n"
                            f"**Your Digital Tickets (General Admission):**\n{tickets_info}\n\n"
                            f"Present your digital QR code at gate entrance for scan verification."
                        )
                        suggestions.append(ChatActionSuggestion(label="Cancel Booking", action_type="cancel_booking", payload={"ref": ref}))
                else:
                    reply = f"🔍 {res.get('message')}"
                return reply, stage, context, suggestions, tool_calls

        # ----------------------------------------------------------------------
        # STAGE 4 & 5: Selection & Booking Request
        # ----------------------------------------------------------------------
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        qty_match = re.search(r"\b([1-9]|10)\s*(tickets?|seats?|tix|ಟಿಕೆಟ್|टिकट)?\b", lower)
        promo_match = re.search(r"\b(TECH20|STUDENT10|EARLYBIRD|FREEPASS)\b", text, re.IGNORECASE)
        promo_code = promo_match.group(1).upper() if promo_match else context.get("promo_code")

        is_book_intent = any(k in lower for k in ["book", "reserve", "buy", "ಬುಕ್", "ಖರೀದಿ", "बुक", "खरीद"]) or email_match

        if is_book_intent and (context.get("selected_event_id") or "event" in lower or "concert" in lower):
            event_id = context.get("selected_event_id")
            tier_id = context.get("selected_tier_id")
            quantity = int(qty_match.group(1)) if qty_match else context.get("selected_quantity", 1)

            # Check business rule: max ticket limit
            try:
                BusinessRulesEngine.validate_ticket_quantity(quantity)
            except ValueError as e:
                return f"⚠️ {str(e)}", "Selection", context, suggestions, tool_calls

            # If user provided promo code, save to context
            if promo_code:
                context["promo_code"] = promo_code

            # If user has not provided email, prompt for customer contact
            if not email_match:
                stage = "Selection"
                context["selected_quantity"] = quantity

                # Calculate live pricing quote
                quote_info = ""
                if tier_id:
                    tool_calls.append(f"calculate_price_quote('{tier_id}', qty={quantity}, promo='{promo_code}')")
                    quote_res = await AgentTools.calculate_price_quote(db, tier_id, quantity, promo_code)
                    if quote_res.get("success"):
                        disc_str = f" (Includes {quote_res.get('discount_description')})" if quote_res.get("discount_description") else ""
                        quote_info = f"\n💵 **Total Price**: {quote_res.get('total_payable')}{disc_str}"

                if lang == "kn":
                    reply = (
                        f"ಉತ್ತಮ! ನಾನು ನಿಮಗಾಗಿ **{quantity} ಸಾಮಾನ್ಯ ಪ್ರವೇಶ (General Admission) ಟಿಕೆಟ್‌ಗಳನ್ನು** ಕಾಯ್ದಿರಿಸುತ್ತಿದ್ದೇನೆ.{quote_info}\n\n"
                        f"ಬುಕಿಂಗ್ ಅಂತಿಮಗೊಳಿಸಲು, ದಯವಿಟ್ಟು ನಿಮ್ಮ **ಪೂರ್ಣ ಹೆಸರು ಮತ್ತು ಇಮೇಲ್ ವಿಳಾಸವನ್ನು** ನೀಡಿ "
                        f"(ಉದಾಹರಣೆಗೆ: *'Book for Adithya, adithya@example.com'*)."
                    )
                elif lang == "hi":
                    reply = (
                        f"बहुत बढ़िया! मैं आपके लिए **{quantity} सामान्य प्रवेश (General Admission) टिकट** सुरक्षित कर रहा हूँ।{quote_info}\n\n"
                        f"बुकिंग पूरी करने के लिए, कृपया अपना **पूरा नाम और ईमेल पता** प्रदान करें "
                        f"(उदाहरण: *'Book for Adithya, adithya@example.com'*)."
                    )
                else:
                    reply = (
                        f"Great! I have held **{quantity} General Admission ticket(s)** for you.{quote_info}\n\n"
                        f"To finalize your booking and acquire your 10-minute hold, please provide your **Full Name and Email Address** "
                        f"(e.g., *'Book for Alex Smith, alex@example.com'*)."
                    )
                return reply, stage, context, suggestions, tool_calls

            # Email was provided! Extract name and process booking
            customer_email = email_match.group(0)
            customer_name = text.split(",")[0].replace("book for", "").replace("Book for", "").replace("book", "").replace("Book", "").strip()
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
                tool_calls.append(f"reserve_and_book_tickets(event='{event_id}', tier='{tier_id}', qty={quantity}, promo='{promo_code}')")
                res = await AgentTools.reserve_and_book_tickets(
                    db=db,
                    event_id=event_id,
                    tier_id=tier_id,
                    quantity=quantity,
                    customer_name=customer_name or "Guest Customer",
                    customer_email=customer_email,
                    promo_code=promo_code
                )

                if res.get("success"):
                    stage = "Confirmation"
                    ref = res["booking_reference"]
                    context["last_booking_ref"] = ref
                    tickets_summary = "\n".join(
                        [f"- Ticket `{t['ticket_code']}` (General Admission)" for t in res.get("tickets", [])]
                    )

                    if lang == "kn":
                        reply = (
                            f"🎉 **ಬುಕಿಂಗ್ ದೃಢೀಕರಿಸಲಾಗಿದೆ! (Booking Confirmed)** (Stage 6: Confirmation)\n\n"
                            f"ನಿಮ್ಮ ಬುಕಿಂಗ್ ಉಲ್ಲೇಖ ಸಂಖ್ಯೆ: **{ref}**\n"
                            f"- **ಕಾರ್ಯಕ್ರಮ**: {context.get('selected_event_title', 'Confirmed Event')}\n"
                            f"- **ಟಿಕೆಟ್ ವರ್ಗ**: {res.get('tier_name')}\n"
                            f"- **ಪ್ರಮಾಣ**: {res.get('quantity')} (ಸಾಮಾನ್ಯ ಪ್ರವೇಶ - General Admission)\n"
                            f"- **ಒಟ್ಟು ಮೊತ್ತ**: {res.get('total_amount')}\n"
                            f"- **ಗ್ರಾಹಕ**: {customer_name} ({customer_email})\n\n"
                            f"**ರಚಿಸಲಾದ ಡಿಜಿಟಲ್ ಟಿಕೆಟ್‌ಗಳು:**\n{tickets_summary}\n\n"
                            f"ಪ್ರವೇಶ ದ್ವಾರದಲ್ಲಿ ಸ್ಕ್ಯಾನ್ ಮಾಡಲು ಗೇಟ್ ಕ್ಯೂಆರ್ ಕೋಡ್ ಸಕ್ರಿಯವಾಗಿದೆ. "
                            f"`{ref}` ಉಲ್ಲೇಖವನ್ನು ಬಳಸಿಕೊಂಡು ನೀವು ಯಾವುದೇ ಸಮಯದಲ್ಲಿ ಈ ಆದೇಶವನ್ನು ಪರಿಶೀಲಿಸಬಹುದು ಅಥವಾ ರದ್ದುಗೊಳಿಸಬಹುದು."
                        )
                        suggestions.append(ChatActionSuggestion(label="ಟಿಕೆಟ್ ಸ್ಥಿತಿ ವೀಕ್ಷಿಸಿ (View Status)", action_type="view_booking", payload={"ref": ref}))
                        suggestions.append(ChatActionSuggestion(label="ಇನ್ನಷ್ಟು ಈವೆಂಟ್‌ಗಳು (More Events)", action_type="discovery", payload={}))
                    elif lang == "hi":
                        reply = (
                            f"🎉 **बुकिंग कन्फर्म हो गई है! (Booking Confirmed)** (Stage 6: Confirmation)\n\n"
                            f"आपका बुकिंग संदर्भ कोड: **{ref}**\n"
                            f"- **कार्यक्रम**: {context.get('selected_event_title', 'Confirmed Event')}\n"
                            f"- **टिकट श्रेणी**: {res.get('tier_name')}\n"
                            f"- **संख्या**: {res.get('quantity')} (सामान्य प्रवेश - General Admission)\n"
                            f"- **कुल देय राशि**: {res.get('total_amount')}\n"
                            f"- **ग्राहक**: {customer_name} ({customer_email})\n\n"
                            f"**जारी किए गए डिजिटल टिकट:**\n{tickets_summary}\n\n"
                            f"प्रवेश द्वार के लिए डिजिटल गेट क्यूआर पास सक्रिय है। "
                            f"आप इस संदर्भ `{ref}` का उपयोग करके कभी भी अपना टिकट देख सकते हैं।"
                        )
                        suggestions.append(ChatActionSuggestion(label="टिकट स्थिति देखें (View Status)", action_type="view_booking", payload={"ref": ref}))
                        suggestions.append(ChatActionSuggestion(label="और कार्यक्रम खोजें (More Events)", action_type="discovery", payload={}))
                    else:
                        reply = (
                            f"🎉 **Booking Confirmed!** (Stage 6: Confirmation)\n\n"
                            f"Your booking reference: **{ref}**\n"
                            f"- **Event**: {context.get('selected_event_title', 'Confirmed Event')}\n"
                            f"- **Tier**: {res.get('tier_name')}\n"
                            f"- **Quantity**: {res.get('quantity')} (General Admission)\n"
                            f"- **Total Paid**: {res.get('total_amount')}\n"
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
        # STAGE 3: Availability & Pricing Inquiry
        # ----------------------------------------------------------------------
        is_avail_intent = any(k in lower for k in [
            "availability", "tickets left", "how many", "price", "pricing", "cost", "discount",
            "ಲಭ್ಯತೆ", "ಬೆಲೆ", "ಎಷ್ಟು", "ದಾಸ್ತಾನು", "ಉಪಲಬ್ಧತಾ", "कीमत", "कितने", "छूट"
        ])
        if is_avail_intent and context.get("selected_event_id"):
            event_id = context.get("selected_event_id")
            tool_calls.append(f"check_ticket_availability('{event_id}')")
            inv = await AgentTools.check_ticket_availability(db, event_id)
            stage = "Availability"

            tiers_md = "\n".join(
                [f"- **{t['tier_name']}**: {t['price']} ({t['status']}) - General Admission" for t in inv.get("tiers", [])]
            )

            # Mention group discount rule & promo codes
            pricing_notes = (
                f"\n💡 **Pricing Engine Benefits**:\n"
                f"- **Group Discount**: 10% off for teams booking 4+ tickets!\n"
                f"- **Promo Codes**: Use `TECH20` (20% off) or `STUDENT10` (10% student discount)."
            )

            if lang == "kn":
                reply = (
                    f"🎫 **{inv.get('event_title', 'Event')} ಗಾಗಿ ರಿಯಲ್-ಟೈಮ್ ಟಿಕೆಟ್ ಲಭ್ಯತೆ** (Stage 3: Availability)\n\n"
                    f"{tiers_md}\n\n"
                    f"**ಒಟ್ಟು ಲಭ್ಯವಿರುವ ಟಿಕೆಟ್‌ಗಳು**: {inv.get('total_available_tickets')}\n"
                    f"{pricing_notes}\n\n"
                    f"ನೀವು ಯಾವ ಟಿಕೆಟ್ ವರ್ಗ ಮತ್ತು ಎಷ್ಟು ಪ್ರಮಾಣವನ್ನು ಆಯ್ಕೆ ಮಾಡಲು ಬಯಸುತ್ತೀರಿ? (ಉದಾ: *'Book 2 tickets'*)"
                )
            elif lang == "hi":
                reply = (
                    f"🎫 **{inv.get('event_title', 'Event')} के लिए लाइव टिकट उपलब्धता** (Stage 3: Availability)\n\n"
                    f"{tiers_md}\n\n"
                    f"**कुल उपलब्ध टिकट**: {inv.get('total_available_tickets')}\n"
                    f"{pricing_notes}\n\n"
                    f"आप किस टिकट श्रेणी और संख्या का चयन करना चाहते हैं? (उदाहरण: *'Book 2 tickets'*)"
                )
            else:
                reply = (
                    f"🎫 **Live Ticket Inventory for {inv.get('event_title', 'Event')}** (Stage 3: Availability)\n\n"
                    f"{tiers_md}\n\n"
                    f"**Total Available Tickets**: {inv.get('total_available_tickets')}\n"
                    f"{pricing_notes}\n\n"
                    f"Which ticket tier and quantity would you like to select? (e.g., *'Book 2 tickets'*)"
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

        # City detection (Indian college cities prioritized, plus fallbacks)
        city_candidate = None
        for c in ["Bengaluru", "Bangalore", "Mysuru", "Hubballi", "New York", "Chicago", "San Francisco"]:
            if c.lower() in lower:
                city_candidate = c
                break

        # Category detection
        category_candidate = None
        for cat in ["Hackathon", "Technical", "Cultural", "Sports", "Workshop", "Conference", "Comedy", "Concert", "Theater"]:
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
                    f"   - 💵 From: {e['starting_price']} (General Admission)\n"
                    f"   - 🏷️ Category: {e['category']}\n\n"
                )

            if lang == "kn":
                reply = (
                    f"👋 **ನಿಮ್ಮ ಹುಡುಕಾಟಕ್ಕೆ ಹೊಂದಿಕೆಯಾಗುವ ಪ್ರಮುಖ ಕಾರ್ಯಕ್ರಮಗಳು:** (Stage 2: Recommendation)\n\n"
                    f"{events_md}"
                    f"ಈ ಕಾರ್ಯಕ್ರಮಗಳ **ರಿಯಲ್-ಟೈಮ್ ಲಭ್ಯತೆ ಮತ್ತು ಬೆಲೆಗಳನ್ನು** ಪರಿಶೀಲಿಸಲು ನೀವು ಬಯಸುತ್ತೀರಾ?"
                )
            elif lang == "hi":
                reply = (
                    f"👋 **आपके अनुरोध से मेल खाने वाले शीर्ष अनुशंसित कार्यक्रम:** (Stage 2: Recommendation)\n\n"
                    f"{events_md}"
                    f"क्या आप इनमें से किसी के लिए **वास्तविक समय टिकट उपलब्धता और कीमतें** देखना चाहते हैं?"
                )
            else:
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
            if lang == "kn":
                reply = (
                    "👋 **AI ಟಿಕೆಟಿಂಗ್ ಮತ್ತು ಬುಕಿಂಗ್ ಸಹಾಯಕಕ್ಕೆ ಸುಸ್ವಾಗತ!**\n\n"
                    "ಕಾಲೇಜು ಹ್ಯಾಕಥಾನ್‌ಗಳು, ತಾಂತ್ರಿಕ ಕಾರ್ಯಕ್ರಮಗಳು, ಸಂಗೀತ ಕಚೇರಿಗಳು ಮತ್ತು ನಾಟಕಗಳನ್ನು ಅನ್ವೇಷಿಸಲು ನಾನು ನಿಮಗೆ ಸಹಾಯ ಮಾಡುತ್ತೇನೆ. "
                    "ನೀವು ಯಾವ ನಗರ ಅಥವಾ ಯಾವ ರೀತಿಯ ಈವೆಂಟ್ ಹುಡುಕುತ್ತಿದ್ದೀರಿ?"
                )
                suggestions.append(ChatActionSuggestion(label="ಬೆಂಗಳೂರು ಹ್ಯಾಕಥಾನ್ (Hackathons)", action_type="search", payload={"city": "Bengaluru", "category": "Hackathon"}))
                suggestions.append(ChatActionSuggestion(label="ಸಾಂಸ್ಕೃತಿಕ ಉತ್ಸವಗಳು (Cultural)", action_type="search", payload={"city": "Bengaluru", "category": "Cultural"}))
            elif lang == "hi":
                reply = (
                    "👋 **AI टिकटिंग और बुकिंग सहायक में आपका स्वागत है!**\n\n"
                    "मैं आपको कॉलेज हैकाथॉन, तकनीकी उत्सव, कॉन्सर्ट और नाटकों की खोज करने में मदद कर सकता हूँ। "
                    "आप किस शहर या किस प्रकार के कार्यक्रम की तलाश कर रहे हैं?"
                )
                suggestions.append(ChatActionSuggestion(label="बेंगलुरु हैकाथॉन (Hackathons)", action_type="search", payload={"city": "Bengaluru", "category": "Hackathon"}))
                suggestions.append(ChatActionSuggestion(label="सांस्कृतिक उत्सव (Cultural)", action_type="search", payload={"city": "Bengaluru", "category": "Cultural"}))
            else:
                reply = (
                    "👋 Welcome to the AI Ticketing & Booking Assistant!\n\n"
                    "I can help you discover collegiate hackathons, technical conferences, cultural fests, and concerts. "
                    "What city or type of event are you looking for?"
                )
                suggestions.append(ChatActionSuggestion(label="Hackathons in Bengaluru", action_type="search", payload={"city": "Bengaluru", "category": "Hackathon"}))
                suggestions.append(ChatActionSuggestion(label="Cultural Fests in Bengaluru", action_type="search", payload={"city": "Bengaluru", "category": "Cultural"}))

        return reply, stage, context, suggestions, tool_calls

    # --------------------------------------------------------------------------
    # LangChain / OpenAI Provider Integration
    # --------------------------------------------------------------------------
    async def _run_openai_agent(
        self,
        db: AsyncSession,
        session: ChatSession,
        user_message: str,
        context: Dict[str, Any],
        lang: str = "en"
    ) -> Tuple[str, str, Dict[str, Any], List[ChatActionSuggestion], List[str]]:
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

            llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.2
            )
            messages = [SystemMessage(content=TICKETING_ASSISTANT_SYSTEM_PROMPT)]
            for m in session.messages[-5:]:
                if m.role == "user":
                    messages.append(HumanMessage(content=m.content))
                elif m.role == "assistant":
                    messages.append(AIMessage(content=m.content))

            messages.append(HumanMessage(content=user_message))
            ai_msg = await llm.ainvoke(messages)
            return ai_msg.content, session.current_stage, context, [], ["openai_llm_invocation"]
        except Exception as e:
            logger.error("OpenAI invocation failed: %s. Falling back to intent engine.", e)
            return await self._run_intent_engine(db, user_message, session.current_stage, context, lang)

    # --------------------------------------------------------------------------
    # Google Gemini Provider Integration
    # --------------------------------------------------------------------------
    async def _run_gemini_agent(
        self,
        db: AsyncSession,
        session: ChatSession,
        user_message: str,
        context: Dict[str, Any],
        lang: str = "en"
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
            return await self._run_intent_engine(db, user_message, session.current_stage, context, lang)


agent_instance = ConversationalTicketingAgent()
