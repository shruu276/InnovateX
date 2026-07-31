"""
utils/dependencies.py — FastAPI dependency callables.

Centralising DI factories here keeps routes thin and makes services
easily swappable for testing (override with app.dependency_overrides).
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.user import User, UserRole, UserStatus
from services.auth import AuthService
from services.project import ProjectService
from services.user import UserService
from utils.security import decode_token

# HTTP Bearer token extractor (reads `Authorization: Bearer <token>`)
_bearer = HTTPBearer(auto_error=True)


# ── Service factories ─────────────────────────────────────────────────────────
def get_auth_service() -> AuthService:
    """Return an AuthService instance. One per request."""
    return AuthService()


def get_user_service() -> UserService:
    """Return a UserService instance. One per request."""
    return UserService()


def get_project_service() -> ProjectService:
    """Return a ProjectService instance. One per request."""
    return ProjectService()


# ── Current-user dependency ────────────────────────────────────────────────────
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode the Bearer JWT and return the matching User object.

    Raises:
        HTTPException 401 — token missing, invalid, or expired.
        HTTPException 401 — user not found in DB (deleted after token issue).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except ValueError:
        raise credentials_exception

    # TODO: replace with a real DB lookup once UserService.get_or_404 is implemented
    # user = await db.get(User, user_id)
    # if user is None:
    #     raise credentials_exception
    # return user
    raise NotImplementedError(
        "TODO: fetch user from DB — uncomment the block above once UserService is implemented."
    )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Like get_current_user but also asserts the account is ACTIVE.

    Raises:
        HTTPException 403 — account suspended or deactivated.
    """
    if current_user.status in (UserStatus.SUSPENDED, UserStatus.DEACTIVATED):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not active.",
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Assert the current user has the ADMIN role.

    Raises:
        HTTPException 403 — non-admin attempting an admin action.
    """
    if current_user.role != UserRole.ADMIN and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required.",
        )
    return current_user
