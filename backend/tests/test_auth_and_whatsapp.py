import pytest
from httpx import AsyncClient
from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token


def test_password_hashing_and_verification():
    plain = "Hackathon@2026"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_token_generation_and_decoding():
    data = {"sub": "student@rvce.edu.in", "role": "customer", "name": "Adithya"}
    token = create_access_token(data)
    assert token is not None

    from app.core.security import decode_access_token
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "student@rvce.edu.in"
    assert payload["role"] == "customer"


@pytest.mark.asyncio
async def test_auth_registration_and_login_flow(client: AsyncClient):
    # 1. Register new user
    reg_payload = {
        "full_name": "Deepak Nesaragi",
        "email": "deepak.dev@example.com",
        "password": "SuperSecretPass123!",
        "phone": "+91-9988776655",
        "role": "organizer",
        "preferred_language": "kn"
    }
    res_reg = await client.post("/api/v1/auth/register", json=reg_payload)
    assert res_reg.status_code == 201
    reg_data = res_reg.json()
    assert "access_token" in reg_data
    assert reg_data["role"] == "organizer"
    assert reg_data["preferred_language"] == "kn"

    # 2. Reject duplicate email registration
    res_dup = await client.post("/api/v1/auth/register", json=reg_payload)
    assert res_dup.status_code == 400

    # 3. Successful login
    login_payload = {
        "email": "deepak.dev@example.com",
        "password": "SuperSecretPass123!"
    }
    res_login = await client.post("/api/v1/auth/login", json=login_payload)
    assert res_login.status_code == 200
    login_data = res_login.json()
    assert "access_token" in login_data
    token = login_data["access_token"]

    # 4. Failed login with wrong password
    res_fail = await client.post("/api/v1/auth/login", json={
        "email": "deepak.dev@example.com",
        "password": "WrongPassword999!"
    })
    assert res_fail.status_code == 401

    # 5. Access protected /auth/me
    headers = {"Authorization": f"Bearer {token}"}
    res_me = await client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 200
    me_data = res_me.json()
    assert me_data["email"] == "deepak.dev@example.com"
    assert me_data["role"] == "organizer"

    # 6. Update user profile
    res_update = await client.put("/api/v1/auth/me", headers=headers, json={
        "full_name": "Deepak Backend Lead",
        "preferred_language": "en"
    })
    assert res_update.status_code == 200
    assert res_update.json()["full_name"] == "Deepak Backend Lead"


@pytest.mark.asyncio
async def test_protected_routes_unauthorized_rejection(client: AsyncClient):
    # Missing token
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 401

    # Invalid token
    res_inv = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer InvalidMalformedToken123"})
    assert res_inv.status_code == 401


@pytest.mark.asyncio
async def test_whatsapp_webhook_challenge(client: AsyncClient):
    challenge = "test_challenge_code_987654"
    verify_token = settings.WHATSAPP_VERIFY_TOKEN

    # Valid challenge
    res = await client.get(
        f"/api/v1/whatsapp/webhook?hub.mode=subscribe&hub.verify_token={verify_token}&hub.challenge={challenge}"
    )
    assert res.status_code == 200
    assert res.text == challenge

    # Invalid token challenge
    res_bad = await client.get(
        f"/api/v1/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=wrong_token&hub.challenge={challenge}"
    )
    assert res_bad.status_code == 403


@pytest.mark.asyncio
async def test_whatsapp_simulation_channel(client: AsyncClient, sample_event_data):
    # Simulate receiving incoming WhatsApp message from student phone
    wa_payload = {
        "sender_phone": "919876543210",
        "message": "Find rock concerts in New York"
    }
    res = await client.post("/api/v1/whatsapp/simulate", json=wa_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["sender_phone"] == "919876543210"
    assert data["session_id"] == "wa_919876543210"
    assert len(data["assistant_reply"]) > 10
    assert data["delivered"] is True
