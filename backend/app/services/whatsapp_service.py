import hmac
import hashlib
import logging
from typing import Optional, Dict, Any, List, Set
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.ai.agent import agent_instance

logger = logging.getLogger("ticketing.whatsapp")

# In-memory deduplication cache for message IDs (backed by 24h retention)
_PROCESSED_MESSAGE_IDS: Set[str] = set()


class WhatsAppService:
    """
    Meta WhatsApp Cloud API Integration Service (Section 2.H).
    - Webhook validation using HMAC-SHA256 signature and app secret.
    - Incoming message parsing & deduplication by message ID.
    - Sender-to-session mapping (wa_{phone}).
    - Forwards to existing AI Conversational Agent (no duplicate bot logic).
    - Dispatches response back to user via WhatsApp Cloud API or simulation.
    """

    @classmethod
    def verify_webhook_signature(cls, payload_bytes: bytes, signature_header: Optional[str]) -> bool:
        """
        Validates the X-Hub-Signature-256 header against the configured WHATSAPP_APP_SECRET.
        """
        if not settings.WHATSAPP_APP_SECRET:
            # If no app secret configured in local dev, allow for development testing
            return True

        if not signature_header:
            logger.warning("WhatsApp webhook missing X-Hub-Signature-256 header.")
            return False

        try:
            expected_hash = signature_header.replace("sha256=", "").strip()
            computed_hash = hmac.new(
                key=settings.WHATSAPP_APP_SECRET.encode("utf-8"),
                msg=payload_bytes,
                digestmod=hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(expected_hash, computed_hash)
        except Exception as e:
            logger.error("Error computing WhatsApp webhook signature: %s", e)
            return False

    @classmethod
    def is_message_duplicate(cls, message_id: str) -> bool:
        """
        Deduplicates incoming Meta webhook deliveries by message ID.
        """
        if message_id in _PROCESSED_MESSAGE_IDS:
            logger.info("Ignoring duplicate WhatsApp message ID: %s", message_id)
            return True
        _PROCESSED_MESSAGE_IDS.add(message_id)
        # Cap set size to prevent memory leaks
        if len(_PROCESSED_MESSAGE_IDS) > 10000:
            _PROCESSED_MESSAGE_IDS.clear()
        return False

    @classmethod
    def extract_messages_from_webhook(cls, payload: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extracts incoming user messages from the Meta WhatsApp Cloud API webhook JSON payload.
        """
        extracted = []
        entries = payload.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    if msg.get("type") == "text":
                        extracted.append({
                            "message_id": msg.get("id"),
                            "sender_phone": msg.get("from"),
                            "text": msg.get("text", {}).get("body", "").strip(),
                            "timestamp": msg.get("timestamp")
                        })
        return extracted

    @classmethod
    async def send_whatsapp_message(cls, to_phone: str, text: str) -> bool:
        """
        Sends an outbound message to the user through Meta WhatsApp Cloud API.
        If credentials are not yet configured in .env, cleanly logs simulated delivery.
        """
        phone_id = settings.WHATSAPP_PHONE_NUMBER_ID
        access_token = settings.WHATSAPP_ACCESS_TOKEN
        api_version = settings.WHATSAPP_API_VERSION

        if phone_id and access_token:
            url = f"https://graph.facebook.com/{api_version}/{phone_id}/messages"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            body = {
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": "text",
                "text": {"body": text}
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(url, headers=headers, json=body)
                    if resp.status_code in [200, 201]:
                        logger.info("WhatsApp message successfully dispatched to %s", to_phone)
                        return True
                    else:
                        logger.error("Meta Graph API returned error %s: %s", resp.status_code, resp.text)
                        return False
            except Exception as e:
                logger.error("Failed to connect to Meta WhatsApp Cloud API: %s", e)
                return False
        else:
            logger.info(
                "[WhatsApp Simulation] Outbound message to %s:\n%s",
                to_phone, text
            )
            return True

    @classmethod
    async def process_whatsapp_message(
        cls,
        db: AsyncSession,
        sender_phone: str,
        message_text: str,
        message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Routes the WhatsApp message to the existing AI Conversational Agent:
        - Stable session ID: wa_{phone}
        - Reuses the existing 7-stage engine (no separate chatbot)
        - Dispatches reply to user
        """
        if message_id and cls.is_message_duplicate(message_id):
            return {
                "status": "DUPLICATE_IGNORED",
                "message_id": message_id,
                "reply": None
            }

        session_id = f"wa_{sender_phone}"
        logger.info("Routing WhatsApp message from %s (Session %s) to AI Agent", sender_phone, session_id)

        # Forward directly to the existing agent
        chat_resp = await agent_instance.process_message(
            db=db,
            user_message=message_text,
            session_id=session_id
        )

        # Dispatch back to WhatsApp
        await cls.send_whatsapp_message(to_phone=sender_phone, text=chat_resp.message)

        return {
            "status": "DELIVERED",
            "session_id": session_id,
            "sender_phone": sender_phone,
            "message": message_text,
            "reply": chat_resp.message,
            "stage": chat_resp.current_stage,
            "language": chat_resp.language
        }
