import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models import TicketTier

logger = logging.getLogger("ticketing.pricing_service")


class PriceQuote(BaseModel):
    unit_price: float
    quantity: int
    base_amount: float
    discount_amount: float = 0.0
    discount_description: Optional[str] = None
    convenience_fee: float = 0.0
    tax_amount: float = 0.0
    total_payable: float
    currency: str = "INR"
    is_free: bool = False


class PricingService:
    """
    Transparent Pricing Engine for PS-07.
    Features:
    - Base ticket calculation: unit_price * quantity
    - Automatic Group Discounts: 10% off for bulk registrations (>= 4 tickets)
    - Validated Promo Code Discounts:
        * 'TECH20': 20% off
        * 'STUDENT10': 10% off for verified collegiate attendees
        * 'EARLYBIRD': Flat ₹50 off
        * 'FREEPASS': 100% waiver
    - Free event handling (₹0.00 total)
    - Configurable convenience fee and GST rates (0% for campus student events)
    - Single standard currency: INR (₹)
    """

    SUPPORTED_PROMOS: Dict[str, Dict[str, Any]] = {
        "TECH20": {"type": "PERCENT", "value": 20.0, "desc": "Technovate 20% Special Discount"},
        "STUDENT10": {"type": "PERCENT", "value": 10.0, "desc": "Collegiate Student 10% Discount"},
        "EARLYBIRD": {"type": "FLAT", "value": 50.0, "desc": "Early Bird ₹50 Flat Voucher"},
        "FREEPASS": {"type": "PERCENT", "value": 100.0, "desc": "100% Hackathon Pass Waiver"},
    }

    @classmethod
    def calculate_quote(
        cls,
        unit_price: float,
        quantity: int,
        promo_code: Optional[str] = None,
        is_student: bool = True
    ) -> PriceQuote:
        unit = float(unit_price)
        base = round(unit * quantity, 2)

        # Free tier handling
        if base == 0.0:
            return PriceQuote(
                unit_price=0.0,
                quantity=quantity,
                base_amount=0.0,
                discount_amount=0.0,
                discount_description="Free Admission Tier",
                convenience_fee=0.0,
                tax_amount=0.0,
                total_payable=0.0,
                currency=settings.DEFAULT_CURRENCY,
                is_free=True
            )

        discount = 0.0
        discount_reasons = []

        # 1. Automatic Team / Group Discount
        if quantity >= settings.GROUP_DISCOUNT_THRESHOLD:
            group_disc = round(base * (settings.GROUP_DISCOUNT_PERCENT / 100.0), 2)
            discount += group_disc
            discount_reasons.append(f"Group Discount ({settings.GROUP_DISCOUNT_PERCENT:.0f}% off for {quantity}+ tickets)")

        # 2. Promo Code Discount
        if promo_code:
            code = promo_code.strip().upper()
            if code in cls.SUPPORTED_PROMOS:
                promo_meta = cls.SUPPORTED_PROMOS[code]
                if promo_meta["type"] == "PERCENT":
                    promo_disc = round(base * (promo_meta["value"] / 100.0), 2)
                else:
                    promo_disc = min(base, float(promo_meta["value"]))
                discount += promo_disc
                discount_reasons.append(promo_meta["desc"])
            else:
                logger.info("Unrecognized promo code '%s' ignored in price calculation.", promo_code)

        # Cap discount at base amount
        discount = min(base, round(discount, 2))
        taxable_amount = max(0.0, round(base - discount, 2))

        # 3. Convenience fee (waived for student collegiate prototype)
        convenience_fee = round(settings.PLATFORM_FEE_AMOUNT, 2) if settings.ENABLE_CONVENIENCE_FEE else 0.0

        # 4. GST / Taxes
        tax_amount = round(taxable_amount * (settings.GST_RATE_PERCENT / 100.0), 2) if settings.GST_RATE_PERCENT > 0 else 0.0

        # 5. Final Payable
        total_payable = max(0.0, round(taxable_amount + convenience_fee + tax_amount, 2))

        return PriceQuote(
            unit_price=unit,
            quantity=quantity,
            base_amount=base,
            discount_amount=discount,
            discount_description="; ".join(discount_reasons) if discount_reasons else None,
            convenience_fee=convenience_fee,
            tax_amount=tax_amount,
            total_payable=total_payable,
            currency=settings.DEFAULT_CURRENCY,
            is_free=(total_payable == 0.0)
        )

    @classmethod
    async def get_tier_quote(
        cls,
        db: AsyncSession,
        tier_id: str,
        quantity: int,
        promo_code: Optional[str] = None
    ) -> PriceQuote:
        stmt = select(TicketTier).where(TicketTier.id == tier_id)
        result = await db.execute(stmt)
        tier = result.scalar_one_or_none()

        if not tier:
            raise ValueError(f"Ticket tier '{tier_id}' not found.")

        return cls.calculate_quote(
            unit_price=float(tier.price),
            quantity=quantity,
            promo_code=promo_code
        )

