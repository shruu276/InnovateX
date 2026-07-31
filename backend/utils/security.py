"""
utils/security.py — JWT creation / validation and password hashing.

All cryptographic operations are centralised here so the rest of the
codebase never imports jose or passlib directly.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from config import settings

# ── Password hashing ──────────────────────────────────────────────────────────
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Return the bcrypt hash of *plain_password*."""
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if *plain_password* matches *hashed_password*."""
    return _pwd_context.verify(plain_password, hashed_password)


# ── JWT helpers ───────────────────────────────────────────────────────────────
def _build_claims(
    subject: str | uuid.UUID,
    extra_claims: Dict[str, Any],
    expires_delta: timedelta,
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    return {
        "sub": str(subject),
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),   # unique token ID (for revocation)
        **extra_claims,
    }


def create_access_token(
    subject: str | uuid.UUID,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a short-lived JWT access token.

    Args:
        subject:      The user's UUID (stored as the ``sub`` claim).
        extra_claims: Optional additional claims (e.g. ``{"role": "admin"}``).
    """
    claims = _build_claims(
        subject=subject,
        extra_claims=extra_claims or {},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: str | uuid.UUID,
) -> str:
    """Create a long-lived JWT refresh token.

    Refresh tokens carry only the ``sub`` and ``jti`` claims; no role data.
    """
    claims = _build_claims(
        subject=subject,
        extra_claims={"type": "refresh"},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT.

    Returns:
        The decoded payload dictionary.

    Raises:
        ValueError: If the token is expired or otherwise invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except ExpiredSignatureError:
        raise ValueError("Token has expired.")
    except JWTError as exc:
        raise ValueError(f"Invalid token: {exc}") from exc


def create_one_time_token(
    subject: str | uuid.UUID,
    purpose: str,
    expires_minutes: int = 60,
) -> str:
    """Create a single-use token for email verification / password reset.

    The ``purpose`` claim should be checked by the consuming endpoint to
    prevent a verify-email token from being used to reset a password.
    """
    claims = _build_claims(
        subject=subject,
        extra_claims={"purpose": purpose},
        expires_delta=timedelta(minutes=expires_minutes),
    )
    return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
