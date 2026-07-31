"""
schemas/user.py — User request / response Pydantic schemas.

Naming convention
-----------------
*Create  → POST body (input, password in plain text)
*Update  → PATCH body (all fields optional)
*Read    → full response including private fields (authenticated owner / admin)
*ReadPublic → stripped response safe to return to any authenticated user
*List    → paginated listing item (compact)
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from pydantic import EmailStr, Field, field_validator, model_validator

from models.user import UserRole, UserStatus
from schemas.common import BaseSchema


# ── Shared field constraints ──────────────────────────────────────────────────
PASSWORD_MIN_LEN = 8
PASSWORD_MAX_LEN = 128


def _validate_password(v: str) -> str:
    """Enforce minimum password complexity rules."""
    if len(v) < PASSWORD_MIN_LEN:
        raise ValueError(f"Password must be at least {PASSWORD_MIN_LEN} characters.")
    if not any(c.isupper() for c in v):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not any(c.isdigit() for c in v):
        raise ValueError("Password must contain at least one digit.")
    return v


# ── Create (registration) ─────────────────────────────────────────────────────
class UserCreate(BaseSchema):
    """Request body for POST /auth/register."""
    email: EmailStr
    password: str = Field(..., min_length=PASSWORD_MIN_LEN, max_length=PASSWORD_MAX_LEN)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str  = Field(..., min_length=1, max_length=100)
    role: UserRole  = UserRole.STUDENT

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return _validate_password(v)


# ── Update (PATCH profile) ────────────────────────────────────────────────────
class UserUpdate(BaseSchema):
    """Request body for PATCH /users/me — all fields optional."""
    first_name: Optional[str]   = Field(None, max_length=100)
    last_name: Optional[str]    = Field(None, max_length=100)
    bio: Optional[str]          = Field(None, max_length=2000)
    institution: Optional[str]  = Field(None, max_length=256)
    department: Optional[str]   = Field(None, max_length=256)
    country: Optional[str]      = Field(None, max_length=100)
    website: Optional[str]      = Field(None, max_length=1024)
    avatar_url: Optional[str]   = Field(None, max_length=1024)


# ── Read (full — owner + admin only) ─────────────────────────────────────────
class UserRead(BaseSchema):
    """Full user profile. Returned to the account owner or an admin."""
    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    full_name: str
    bio: Optional[str]
    avatar_url: Optional[str]
    institution: Optional[str]
    department: Optional[str]
    country: Optional[str]
    website: Optional[str]
    role: UserRole
    status: UserStatus
    is_verified: bool
    is_mfa_enabled: bool
    innovation_score: int


# ── Read (public — safe for any authenticated user) ────────────────────────────
class UserReadPublic(BaseSchema):
    """Public-facing profile — PII-reduced."""
    id: uuid.UUID
    first_name: str
    last_name: str
    full_name: str
    bio: Optional[str]
    avatar_url: Optional[str]
    institution: Optional[str]
    country: Optional[str]
    role: UserRole
    innovation_score: int


# ── List item ─────────────────────────────────────────────────────────────────
class UserList(BaseSchema):
    """Compact representation used in paginated list responses."""
    id: uuid.UUID
    full_name: str
    email: EmailStr
    role: UserRole
    status: UserStatus
    innovation_score: int


# ── Password operations ───────────────────────────────────────────────────────
class PasswordChange(BaseSchema):
    """Request body for POST /users/me/password."""
    current_password: str
    new_password: str = Field(..., min_length=PASSWORD_MIN_LEN, max_length=PASSWORD_MAX_LEN)

    @field_validator("new_password")
    @classmethod
    def new_password_strength(cls, v: str) -> str:
        return _validate_password(v)


class PasswordReset(BaseSchema):
    """Request body for POST /auth/password-reset (unauthenticated)."""
    email: EmailStr


class PasswordResetConfirm(BaseSchema):
    """Request body for POST /auth/password-reset/confirm."""
    token: str
    new_password: str = Field(..., min_length=PASSWORD_MIN_LEN, max_length=PASSWORD_MAX_LEN)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return _validate_password(v)
