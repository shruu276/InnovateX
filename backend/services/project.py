"""
services/project.py — Project management business logic.

All methods are stubbed with clear TODO comments and documented contracts.
"""

from __future__ import annotations

import uuid
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.project import Project, ProjectStatus, ProjectVisibility
from models.user import User, UserRole
from schemas.project import ProjectCreate, ProjectUpdate
from utils.pagination import PaginationParams


class ProjectService:
    """Encapsulates all project management operations.

    Injected via `utils.dependencies.get_project_service`.
    """

    # ── Create ────────────────────────────────────────────────────────────────
    async def create(
        self,
        db: AsyncSession,
        payload: ProjectCreate,
        owner: User,
    ) -> Project:
        """
        Create a new project owned by `owner`.

        Steps (to implement):
            1. Generate a unique URL slug from the title.
            2. Instantiate Project(**payload.model_dump(), owner_id=owner.id).
            3. db.add(project); await db.flush(); await db.refresh(project).
            4. Return project.

        Raises:
            HTTPException 409 — if slug collision cannot be resolved.
        """
        raise NotImplementedError("TODO: implement create()")

    # ── Fetch ─────────────────────────────────────────────────────────────────
    async def get_or_404(
        self,
        db: AsyncSession,
        project_id: uuid.UUID,
        requesting_user: User,
    ) -> Project:
        """
        Fetch a project by UUID, enforcing visibility rules.

        Visibility rules:
            PUBLIC   → any authenticated user
            TEAM     → team members only
            PRIVATE  → owner and admins only

        Raises:
            HTTPException 404 — project not found.
            HTTPException 403 — insufficient permissions.
        """
        raise NotImplementedError("TODO: implement get_or_404()")

    # ── List ──────────────────────────────────────────────────────────────────
    async def list_for_user(
        self,
        db: AsyncSession,
        user: User,
        pagination: PaginationParams,
        *,
        status_filter: Optional[str] = None,
        domain: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Project], int]:
        """
        Return paginated projects visible to `user`.

        Steps (to implement):
            Build a SELECT with WHERE clauses:
            - (visibility = PUBLIC) OR (owner_id = user.id) OR (user in team)
            - Apply status_filter, domain, full-text search if provided.
            - Apply pagination offset / limit.
            - Return (projects, total_count).
        """
        raise NotImplementedError("TODO: implement list_for_user()")

    # ── Update ────────────────────────────────────────────────────────────────
    async def update(
        self,
        db: AsyncSession,
        project_id: uuid.UUID,
        payload: ProjectUpdate,
        requesting_user: User,
    ) -> Project:
        """
        Apply partial updates. Only owner or ADMIN role may update.

        Raises:
            HTTPException 403 — not the owner and not an admin.
            HTTPException 404 — project not found.
        """
        raise NotImplementedError("TODO: implement update()")

    # ── Archive ───────────────────────────────────────────────────────────────
    async def archive(
        self,
        db: AsyncSession,
        project_id: uuid.UUID,
        requesting_user: User,
    ) -> None:
        """
        Soft-delete: set status = ARCHIVED.

        Raises:
            HTTPException 403 — not the owner and not an admin.
            HTTPException 404 — project not found.
        """
        raise NotImplementedError("TODO: implement archive()")

    # ── Publish ───────────────────────────────────────────────────────────────
    async def publish(
        self,
        db: AsyncSession,
        project_id: uuid.UUID,
        requesting_user: User,
    ) -> Project:
        """
        Set visibility = PUBLIC, status = ACTIVE.

        Raises:
            HTTPException 403 — not the owner.
            HTTPException 404 — project not found.
            HTTPException 422 — project is missing required fields (title, description).
        """
        raise NotImplementedError("TODO: implement publish()")

    # ── Internal helpers ──────────────────────────────────────────────────────
    @staticmethod
    def _assert_owner_or_admin(project: Project, user: User) -> None:
        """Raise 403 if `user` is neither the project owner nor a platform admin."""
        if str(project.owner_id) != str(user.id) and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this project.",
            )
