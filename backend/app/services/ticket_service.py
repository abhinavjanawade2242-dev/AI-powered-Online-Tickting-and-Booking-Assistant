import base64
import hashlib
import hmac
import io
from typing import Optional
import qrcode


class TicketService:
    @staticmethod
    def create_qr_code_base64(qr_payload: str) -> str:
        """
        Generate a high-density base64 encoded PNG QR code image
        from the tamper-evident payload for mobile display or print.
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=2,
        )
        qr.add_data(qr_payload)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    @staticmethod
    def verify_qr_payload(qr_payload: str) -> bool:
        """Verify the integrity and signature of a gate-scanned QR payload."""
        parts = qr_payload.split("|")
        if len(parts) < 6:
            return False
        ticket_code, booking_ref, event_id, tier_name, timestamp, signature = parts[:6]
        raw_payload = f"{ticket_code}|{booking_ref}|{event_id}|{tier_name}|{timestamp}"
        expected_signature = hashlib.sha256(raw_payload.encode()).hexdigest()[:12]
        return hmac.compare_digest(signature, expected_signature)

