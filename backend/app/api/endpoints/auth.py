import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.models import User
from app.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserProfileResponse,
    UserUpdateRequest,
)

logger = logging.getLogger("ticketing.auth")
router = APIRouter(prefix="/auth", tags=["Section A: Authentication & User Management"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, summary="Register customer/organizer account")
async def register_user(
    req: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Section 2.A: Register a new customer, organizer, or admin user.
    - Hashes password securely using bcrypt.
    - Generates signed JWT access token.
    """
    email_clean = req.email.strip().lower()
    stmt = select(User).where(User.email == email_clean)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user and existing_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please log in."
        )

    hashed_pw = hash_password(req.password)
    user_role = req.role if req.role in ["customer", "organizer", "admin"] else "customer"

    if existing_user:
        # Upgrade guest record to full registered user
        existing_user.full_name = req.full_name
        existing_user.password_hash = hashed_pw
        existing_user.role = user_role
        existing_user.preferred_language = req.preferred_language or "en"
        if req.phone:
            existing_user.phone = req.phone
        user = existing_user
    else:
        user = User(
            full_name=req.full_name,
            email=email_clean,
            password_hash=hashed_pw,
            role=user_role,
            preferred_language=req.preferred_language or "en",
            phone=req.phone
        )
        db.add(user)

    await db.commit()
    await db.refresh(user)

    token_data = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role,
        "name": user.full_name
    }
    access_token = create_access_token(token_data, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    logger.info("New user registered successfully: %s (%s)", user.email, user.role)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        preferred_language=user.preferred_language
    )


@router.post("/login", response_model=TokenResponse, summary="Authenticate and obtain JWT bearer token")
async def login_user(
    req: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Section 2.A: Authenticate registered user credentials.
    - Verifies bcrypt password hash.
    - Issues a signed JWT access token.
    """
    email_clean = req.email.strip().lower()
    stmt = select(User).where(User.email == email_clean)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not user.password_hash or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please verify your credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role,
        "name": user.full_name
    }
    access_token = create_access_token(token_data, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    logger.info("User logged in successfully: %s", user.email)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        preferred_language=user.preferred_language
    )


@router.get("/me", response_model=UserProfileResponse, summary="Get current user profile (Protected)")
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Section 2.A: Retrieve current authenticated user profile.
    Requires Bearer token authorization header.
    """
    return UserProfileResponse.model_validate(current_user)


@router.put("/me", response_model=UserProfileResponse, summary="Update current user profile (Protected)")
async def update_my_profile(
    req: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Section 2.A: Update current user's profile details.
    """
    if req.full_name is not None:
        current_user.full_name = req.full_name.strip()
    if req.phone is not None:
        current_user.phone = req.phone.strip()
    if req.preferred_language is not None and req.preferred_language in ["en", "kn", "hi"]:
        current_user.preferred_language = req.preferred_language

    await db.commit()
    await db.refresh(current_user)
    return UserProfileResponse.model_validate(current_user)
