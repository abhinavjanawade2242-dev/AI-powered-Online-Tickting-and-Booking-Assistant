import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from app.core.config import settings
from app.services.business_rules import BusinessRulesEngine
from app.services.pricing_service import PricingService


def test_business_rules_ticket_quantity_limits():
    # Valid quantity
    BusinessRulesEngine.validate_ticket_quantity(1)
    BusinessRulesEngine.validate_ticket_quantity(6)

    # Invalid: 0 or negative
    with pytest.raises(ValueError, match="at least 1"):
        BusinessRulesEngine.validate_ticket_quantity(0)
    with pytest.raises(ValueError, match="at least 1"):
        BusinessRulesEngine.validate_ticket_quantity(-2)

    # Invalid: exceeding max limit (default 6)
    with pytest.raises(ValueError, match="exceeds the maximum allowed limit"):
        BusinessRulesEngine.validate_ticket_quantity(7)


def test_business_rules_hold_expiration():
    now = datetime.utcnow()
    hold_time = BusinessRulesEngine.calculate_hold_expiration(minutes=10)
    assert hold_time > now
    assert (hold_time - now).total_seconds() >= 590

    # Test is_hold_expired
    past_hold = now - timedelta(minutes=1)
    assert BusinessRulesEngine.is_hold_expired(past_hold, now=now) is True

    future_hold = now + timedelta(minutes=5)
    assert BusinessRulesEngine.is_hold_expired(future_hold, now=now) is False


def test_business_rules_24h_cancellation_policy():
    now = datetime.utcnow()

    # Case 1: Event starts in 30 hours (> 24h) -> Eligible
    eligible_event_time = now + timedelta(hours=30)
    is_eligible, msg = BusinessRulesEngine.validate_cancellation_eligibility(eligible_event_time, now=now)
    assert is_eligible is True
    assert "Eligible for cancellation" in msg

    # Case 2: Event starts in 12 hours (< 24h) -> Ineligible
    ineligible_event_time = now + timedelta(hours=12)
    is_eligible2, msg2 = BusinessRulesEngine.validate_cancellation_eligibility(ineligible_event_time, now=now)
    assert is_eligible2 is False
    assert "at least 24 hours prior" in msg2

    # Case 3: 100% Refund calculation
    refund_amt, refund_stat = BusinessRulesEngine.calculate_cancellation_refund(498.0, is_eligible=True)
    assert refund_amt == 498.0
    assert refund_stat == "REFUNDED"

    refund_amt_no, refund_stat_no = BusinessRulesEngine.calculate_cancellation_refund(498.0, is_eligible=False)
    assert refund_amt_no == 0.0
    assert refund_stat_no == "NOT_ELIGIBLE"


def test_pricing_engine_standard_and_free():
    # 1. Standard calculation
    quote = PricingService.calculate_quote(unit_price=250.0, quantity=2)
    assert quote.base_amount == 500.0
    assert quote.discount_amount == 0.0
    assert quote.total_payable == 500.0
    assert quote.currency == "INR"
    assert quote.is_free is False

    # 2. Free event calculation
    free_quote = PricingService.calculate_quote(unit_price=0.0, quantity=3)
    assert free_quote.base_amount == 0.0
    assert free_quote.total_payable == 0.0
    assert free_quote.is_free is True


def test_pricing_engine_group_discount():
    # 4 or more tickets triggers 10% group discount
    quote = PricingService.calculate_quote(unit_price=100.0, quantity=4)
    assert quote.base_amount == 400.0
    assert quote.discount_amount == 40.0  # 10% of 400
    assert quote.total_payable == 360.0
    assert "Group Discount" in (quote.discount_description or "")


def test_pricing_engine_promo_codes():
    # TECH20 (20% off)
    quote1 = PricingService.calculate_quote(unit_price=500.0, quantity=1, promo_code="TECH20")
    assert quote1.discount_amount == 100.0  # 20% of 500
    assert quote1.total_payable == 400.0

    # STUDENT10 (10% off)
    quote2 = PricingService.calculate_quote(unit_price=200.0, quantity=1, promo_code="STUDENT10")
    assert quote2.discount_amount == 20.0
    assert quote2.total_payable == 180.0

    # EARLYBIRD (Flat ₹50 off)
    quote3 = PricingService.calculate_quote(unit_price=300.0, quantity=1, promo_code="EARLYBIRD")
    assert quote3.discount_amount == 50.0
    assert quote3.total_payable == 250.0

    # FREEPASS (100% off)
    quote4 = PricingService.calculate_quote(unit_price=350.0, quantity=1, promo_code="FREEPASS")
    assert quote4.discount_amount == 350.0
    assert quote4.total_payable == 0.0
    assert quote4.is_free is True


@pytest.mark.asyncio
async def test_pricing_api_endpoints(client: AsyncClient, sample_event_data):
    tier_id = sample_event_data["tier_vip"].id

    # 1. Price quote API
    res = await client.post("/api/v1/pricing/quote", json={
        "tier_id": tier_id,
        "quantity": 4,
        "promo_code": "TECH20"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["currency"] == "INR"
    assert data["quantity"] == 4
    assert data["discount_amount"] > 0
    assert data["total_payable"] < data["base_amount"]

    # 2. Get active promos API
    res_promos = await client.get("/api/v1/pricing/promos")
    assert res_promos.status_code == 200
    promos = res_promos.json()
    assert any(p["code"] == "TECH20" for p in promos)


@pytest.mark.asyncio
async def test_multilingual_ai_agent(client: AsyncClient, sample_event_data):
    session_id = "test_multilingual_session_999"

    # Turn 1 (Kannada Discovery): User asks in Kannada
    res_kn = await client.post("/api/v1/chat", json={
        "message": "ನಮಸ್ಕಾರ, ಬೆಂಗಳೂರಿನಲ್ಲಿ ನಡೆಯುವ ಹ್ಯಾಕಥಾನ್ ಅಥವಾ ಸಂಗೀತ ಕಾರ್ಯಕ್ರಮ ತಿಳಿಸಿ",
        "session_id": session_id,
        "language": "kn"
    })
    assert res_kn.status_code == 200
    data_kn = res_kn.json()
    assert data_kn["language"] == "kn"
    # Validates Kannada response text
    assert any(w in data_kn["message"] for w in ["ಕಾರ್ಯಕ್ರಮ", "ಲಭ್ಯತೆ", "ಬೆಂಗಳೂರು", "Rock Fest", "Technovate", "ಸ್ವಾಗತ"])

    # Turn 2 (Hindi Discovery): User asks in Hindi
    res_hi = await client.post("/api/v1/chat", json={
        "message": "नमस्ते, मुझे रॉक कॉन्सर्ट या इवेंट के बारे में बताएं",
        "session_id": "test_hindi_session_888",
        "language": "hi"
    })
    assert res_hi.status_code == 200
    data_hi = res_hi.json()
    assert data_hi["language"] == "hi"
    # Validates Hindi response text
    assert any(w in data_hi["message"] for w in ["कार्यक्रम", "उपलब्धता", "स्वागत", "Rock Fest"])
