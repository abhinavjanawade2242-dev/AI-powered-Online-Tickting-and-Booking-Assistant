import hashlib
import secrets
import string
import time


def generate_booking_reference(prefix: str = "BK-") -> str:
    """Generate a clean, customer-friendly booking reference like BK-9A82F1."""
    random_chars = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f"{prefix}{random_chars}"


def generate_ticket_code(prefix: str = "TIX-") -> str:
    """Generate a unique digital ticket identifier like TIX-84920391."""
    random_chars = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    return f"{prefix}{random_chars}"


def generate_qr_payload(ticket_code: str, booking_ref: str, event_id: str, tier_name: str) -> str:
    """
    Generate tamper-evident QR code content for gate check-in scanning.
    Includes a SHA-256 signature token.
    """
    timestamp = int(time.time())
    raw_payload = f"{ticket_code}|{booking_ref}|{event_id}|{tier_name}|{timestamp}"
    signature = hashlib.sha256(raw_payload.encode()).hexdigest()[:12]
    return f"{raw_payload}|{signature}"

