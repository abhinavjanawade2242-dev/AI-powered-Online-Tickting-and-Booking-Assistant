import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional
from app.core.config import settings

logger = logging.getLogger("ticketing.business_rules")


class BusinessRulesEngine:
    """
    Centralized Business Rules Engine for PS-07.
    Enforces all core domain rules:
    - Configurable ticket limits per booking (default 6).
    - Configurable reservation hold duration (default 10 minutes).
    - 24-hour advance cancellation rule with exact boundary checks.
    - 100% Sandbox refund rule for eligible cancellations.
    - Mandatory General Admission enforcement (no assigned seats).
    - Single-currency enforcement (INR / ₹).
    - Payment simulation lifecycle transitions.
    """

    @staticmethod
    def validate_ticket_quantity(
        quantity: int,
        max_limit: Optional[int] = None
    ) -> None:
        """
        Rule: Customers select ticket quantities up to a configurable maximum limit.
        Admin configurable via settings.MAX_TICKETS_PER_BOOKING.
        """
        limit = max_limit or settings.MAX_TICKETS_PER_BOOKING
        if quantity < 1:
            raise ValueError("Ticket quantity must be at least 1.")
        if quantity > limit:
            raise ValueError(
                f"Requested quantity {quantity} exceeds the maximum allowed limit of "
                f"{limit} tickets per booking. Please reduce your quantity."
            )

    @staticmethod
    def calculate_hold_expiration(
        minutes: Optional[int] = None
    ) -> datetime:
        """
        Rule: Establishes a temporary reservation hold (default: 10 minutes).
        Configurable via settings.HOLD_DURATION_MINUTES or settings.RESERVATION_HOLD_TTL_SECONDS.
        """
        duration = minutes or settings.HOLD_DURATION_MINUTES
        return datetime.utcnow() + timedelta(minutes=duration)

    @staticmethod
    def is_hold_expired(
        hold_expires_at: Optional[datetime],
        now: Optional[datetime] = None
    ) -> bool:
        """
        Rule: Checks whether a reservation hold has expired.
        """
        if not hold_expires_at:
            return False
        current_time = now or datetime.utcnow()
        return current_time > hold_expires_at

    @staticmethod
    def validate_cancellation_eligibility(
        event_start_time: datetime,
        now: Optional[datetime] = None,
        window_hours: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Rule: 24-Hour Advance Cancellation Policy.
        Cancellations are allowed only if the event start time is at least 24 hours in the future.
        Boundary condition: exactly 24 hours or more -> ALLOWED; less than 24 hours -> REJECTED.
        """
        current_time = now or datetime.utcnow()
        required_hours = window_hours if window_hours is not None else settings.CANCELLATION_WINDOW_HOURS
        time_until_event = event_start_time - current_time

        if time_until_event < timedelta(hours=required_hours):
            hours_left = max(0.0, time_until_event.total_seconds() / 3600.0)
            msg = (
                f"Cancellations are only permitted at least {required_hours} hours prior to event start time. "
                f"Event starts in {hours_left:.1f} hours."
            )
            return False, msg

        return True, f"Eligible for cancellation and 100% refund (starts in {time_until_event.total_seconds() / 3600.0:.1f} hours)."

    @staticmethod
    def calculate_cancellation_refund(
        total_amount: float,
        is_eligible: bool
    ) -> Tuple[float, str]:
        """
        Rule: 100% Sandbox Refund on Eligible Cancellation.
        When eligible, full purchase price is refunded.
        """
        if not is_eligible:
            return 0.0, "NOT_ELIGIBLE"
        return float(total_amount), "REFUNDED"

    @staticmethod
    def validate_currency(currency: str) -> None:
        """
        Rule: Strictly INR (₹). Foreign currencies are prohibited.
        """
        if currency.strip().upper() != settings.DEFAULT_CURRENCY:
            raise ValueError(
                f"Invalid currency '{currency}'. The platform exclusively operates in {settings.DEFAULT_CURRENCY} (₹)."
            )

    @staticmethod
    def validate_payment_callback(
        booking_status: str,
        hold_expires_at: Optional[datetime],
        now: Optional[datetime] = None
    ) -> Tuple[bool, str]:
        """
        Rule: Late payment callback after inventory lock expiry.
        If payment callback arrives after hold expired, payment is rejected or auto-refunded;
        tickets are never issued.
        """
        if booking_status == "CONFIRMED":
            return True, "Booking already confirmed."

        if BusinessRulesEngine.is_hold_expired(hold_expires_at, now):
            return False, "Reservation hold expired before payment confirmation. Inventory has been released."

        return True, "Hold is valid. Proceed to confirm."

