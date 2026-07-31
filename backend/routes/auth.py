"""
routes/auth.py — Authentication endpoints.

POST /auth/register      → create account
POST /auth/login         → obtain access + refresh tokens
POST /auth/refresh       → rotate refresh token
POST /auth/logout        → invalidate refresh token
POST /auth/verify-email  → confirm email address
POST /auth/password-reset          → request reset link
POST /auth/password-reset/confirm  → apply new password
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import (
    MessageResponse, PasswordReset, PasswordResetConfirm,
    RefreshRequest, Token, TokenPair, UserCreate, UserRead,
)
from services.auth import AuthService
from utils.dependencies import get_auth_service

router = APIRouter(prefix="/auth")


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new account",
)
async def register(
    payload: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    svc: AuthService = Depends(get_auth_service),
) -> UserRead:
    """Create a new user account and send a verification email."""
    return await svc.register(db, payload, background_tasks)


@router.post(
    "/login",
    response_model=TokenPair,
    summary="Login with email and password",
)
async def login(
    payload: UserCreate,    # reusing create schema for brevity; swap for OAuth2PasswordRequestForm in production
    db: AsyncSession = Depends(get_db),
    svc: AuthService = Depends(get_auth_service),
) -> TokenPair:
    """Authenticate and return an access + refresh token pair."""
    return await svc.login(db, payload.email, payload.password)


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Rotate refresh token",
)
async def refresh_tokens(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    svc: AuthService = Depends(get_auth_service),
) -> TokenPair:
    """Exchange a valid refresh token for a new access + refresh token pair."""
    return await svc.refresh(db, payload.refresh_token)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout (invalidate refresh token)",
)
async def logout(
    payload: RefreshRequest,
    svc: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """Revoke the provided refresh token so it cannot be reused."""
    await svc.logout(payload.refresh_token)
    return MessageResponse(message="Logged out successfully.")


@router.post(
    "/verify-email",
    response_model=MessageResponse,
    summary="Verify email address",
)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
    svc: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """Confirm the user's email address using the one-time verification token."""
    await svc.verify_email(db, token)
    return MessageResponse(message="Email verified successfully.")


@router.post(
    "/password-reset",
    response_model=MessageResponse,
    summary="Request password reset link",
)
async def request_password_reset(
    payload: PasswordReset,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    svc: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """Send a password-reset email if the address is registered."""
    await svc.request_password_reset(db, payload.email, background_tasks)
    # Always return 200 to avoid user-enumeration attacks
    return MessageResponse(message="If that email is registered, a reset link has been sent.")


@router.post(
    "/password-reset/confirm",
    response_model=MessageResponse,
    summary="Confirm password reset",
)
async def confirm_password_reset(
    payload: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
    svc: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """Apply a new password using a valid reset token."""
    await svc.confirm_password_reset(db, payload.token, payload.new_password)
    return MessageResponse(message="Password updated successfully.")
