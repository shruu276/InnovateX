"""
routes/users.py — User profile and account management endpoints.

GET    /users/me              → current user profile
PATCH  /users/me              → update profile
POST   /users/me/password     → change password
DELETE /users/me              → deactivate account
GET    /users/{user_id}       → public profile
GET    /users                 → admin: list all users (paginated)
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.user import User
from schemas import (
    MessageResponse, PaginatedResponse, PasswordChange,
    UserList, UserRead, UserReadPublic, UserUpdate,
)
from services.user import UserService
from utils.dependencies import get_current_active_user, get_user_service, require_admin
from utils.pagination import PaginationParams

router = APIRouter(prefix="/users")


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user profile",
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> UserRead:
    """Return the full profile of the authenticated user."""
    return UserRead.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserRead,
    summary="Update current user profile",
)
async def update_me(
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    svc: UserService = Depends(get_user_service),
) -> UserRead:
    """Partially update the authenticated user's profile."""
    updated = await svc.update(db, current_user, payload)
    return UserRead.model_validate(updated)


@router.post(
    "/me/password",
    response_model=MessageResponse,
    summary="Change password",
)
async def change_password(
    payload: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    svc: UserService = Depends(get_user_service),
) -> MessageResponse:
    """Change the authenticated user's password (requires current password)."""
    await svc.change_password(db, current_user, payload)
    return MessageResponse(message="Password changed successfully.")


@router.delete(
    "/me",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Deactivate account",
)
async def deactivate_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    svc: UserService = Depends(get_user_service),
) -> MessageResponse:
    """Soft-delete the account (sets status to DEACTIVATED)."""
    await svc.deactivate(db, current_user)
    return MessageResponse(message="Account deactivated.")


@router.get(
    "/{user_id}",
    response_model=UserReadPublic,
    summary="Get public profile",
)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),   # must be authenticated
    svc: UserService = Depends(get_user_service),
) -> UserReadPublic:
    """Return the public profile of any user by UUID."""
    user = await svc.get_or_404(db, user_id)
    return UserReadPublic.model_validate(user)


# ── Admin-only ────────────────────────────────────────────────────────────────
@router.get(
    "",
    response_model=PaginatedResponse[UserList],
    summary="[Admin] List all users",
    dependencies=[Depends(require_admin)],
)
async def list_users(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(),
    svc: UserService = Depends(get_user_service),
) -> PaginatedResponse[UserList]:
    """Paginated list of all platform users. Admin only."""
    users, total = await svc.list_all(db, pagination)
    items = [UserList.model_validate(u) for u in users]
    return PaginatedResponse.create(items, total, pagination.page, pagination.size)
