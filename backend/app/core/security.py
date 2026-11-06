import hashlib
import secrets
import string
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models import User

security_scheme = HTTPBearer(auto_error=False)


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


# ------------------------------------------------------------------------------
# Password Hashing & Validation (bcrypt)
# ------------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    if not hashed_password:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


# ------------------------------------------------------------------------------
# JWT Token Generation & Validation (PyJWT)
# ------------------------------------------------------------------------------

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except (jwt.PyJWTError, Exception):
        return None


# ------------------------------------------------------------------------------
# FastAPI Authentication & RBAC Dependencies
# ------------------------------------------------------------------------------

async def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency that enforces valid JWT authentication and returns current User.
    Raises HTTP 401 if token is missing or invalid.
    """
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(auth.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_email = payload["sub"]
    stmt = select(User).where(User.email == user_email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_optional_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Dependency that returns current User if token is provided, or None if anonymous.
    """
    if not auth or not auth.credentials:
        return None

    payload = decode_access_token(auth.credentials)
    if not payload or "sub" not in payload:
        return None

    stmt = select(User).where(User.email == payload["sub"])
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def require_role(allowed_roles: List[str]):
    """
    Role-Based Access Control (RBAC) dependency factory.
    Example: Depends(require_role(["admin", "organizer"]))
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Operation requires one of roles {allowed_roles}. Current role: '{current_user.role}'."
            )
        return current_user

    return role_checker
