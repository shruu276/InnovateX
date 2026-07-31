"""
schemas/token.py — JWT token Pydantic schemas.
"""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import Field

from schemas.common import BaseSchema


class Token(BaseSchema):
    """Returned by /auth/login — short-lived access token only."""
    access_token: str
    token_type: str = "bearer"


class TokenPair(BaseSchema):
    """Returned by endpoints that also issue a refresh token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseSchema):
    """Request body for POST /auth/refresh."""
    refresh_token: str


class TokenData(BaseSchema):
    """Decoded payload extracted from a validated JWT.

    This is **internal** — never serialised to API responses.
    """
    sub: uuid.UUID = Field(..., description="User ID (subject claim)")
    role: Optional[str] = None
    jti: Optional[str] = Field(None, description="JWT ID — used for refresh token rotation")
    exp: Optional[int] = None
