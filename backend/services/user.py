"""
services/user.py — User profile management business logic.

All methods are stubbed with clear TODO comments and documented
parameter / return contracts.
"""

from __future__ import annotations

import uuid
from typing import List, Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserStatus
from schemas.user import PasswordChange, UserUpdate
from utils.pagination import PaginationParams


class UserService:
    """Encapsulates user profile management operations.

    Injected via `utils.dependencies.get_user_service`.
    """

    # ── Fetch ─────────────────────────────────────────────────────────────────
    async def get_or_404(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> User:
        """
        Fetch a user by primary key or raise 404.

        Steps (to implement):
            result = await db.get(User, user_id)
            if not result or result.status == UserStatus.DEACTIVATED:
                raise HTTPException(status_code=404, detail="User not found.")
            return result

        Raises:
            HTTPException 404 — user does not exist or is deactivated.
        """
        raise NotImplementedError("TODO: implement get_or_404()")

    # ── Update ────────────────────────────────────────────────────────────────
    async def update(
        self,
        db: AsyncSession,
        user: User,
        payload: UserUpdate,
    ) -> User:
        """
        Apply partial updates to the user's profile.

        Steps (to implement):
            update_data = payload.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)
            db.add(user)
            await db.flush()
            await db.refresh(user)
            return user
        """
        raise NotImplementedError("TODO: implement update()")

    # ── Password change ───────────────────────────────────────────────────────
    async def change_password(
        self,
        db: AsyncSession,
        user: User,
        payload: PasswordChange,
    ) -> None:
        """
        Verify current password and apply the new hash.

        Raises:
            HTTPException 400 — current password is incorrect.
        """
        raise NotImplementedError("TODO: implement change_password()")

    # ── Deactivation ──────────────────────────────────────────────────────────
    async def deactivate(
        self,
        db: AsyncSession,
        user: User,
    ) -> None:
        """
        Soft-delete: set status = DEACTIVATED and anonymise PII.

        Steps (to implement):
            user.status = UserStatus.DEACTIVATED
            user.email = f"deleted_{user.id}@deactivated.invalid"
            db.add(user)
            await db.flush()
        """
        raise NotImplementedError("TODO: implement deactivate()")

    # ── Admin listing ─────────────────────────────────────────────────────────
    async def list_all(
        self,
        db: AsyncSession,
        pagination: PaginationParams,
    ) -> Tuple[List[User], int]:
        """
        Return a paginated list of all users and the total count.

        Steps (to implement):
            from sqlalchemy import func, select
            count_q = select(func.count()).select_from(User)
            total = (await db.execute(count_q)).scalar_one()
            users_q = select(User).offset(pagination.offset).limit(pagination.size)
            users = list((await db.execute(users_q)).scalars().all())
            return users, total
        """
        raise NotImplementedError("TODO: implement list_all()")
