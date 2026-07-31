"""
routes/projects.py — Project CRUD endpoints.

POST   /projects                     → create project
GET    /projects                     → list (paginated, filtered)
GET    /projects/{project_id}        → get detail
PATCH  /projects/{project_id}        → update (owner / admin)
DELETE /projects/{project_id}        → soft-delete (owner / admin)
POST   /projects/{project_id}/publish → publish (make public)
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.user import User
from schemas import (
    MessageResponse, PaginatedResponse,
    ProjectCreate, ProjectList, ProjectRead, ProjectUpdate,
)
from services.project import ProjectService
from utils.dependencies import (
    get_current_active_user,
    get_project_service,
)
from utils.pagination import PaginationParams

router = APIRouter(prefix="/projects")


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    svc: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    """Create a new project owned by the authenticated user."""
    project = await svc.create(db, payload, current_user)
    return ProjectRead.model_validate(project)


@router.get(
    "",
    response_model=PaginatedResponse[ProjectList],
    summary="List projects",
)
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    pagination: PaginationParams = Depends(),
    status_filter: Optional[str] = Query(None, alias="status"),
    domain: Optional[str] = Query(None),
    search: Optional[str] = Query(None, max_length=256),
    svc: ProjectService = Depends(get_project_service),
) -> PaginatedResponse[ProjectList]:
    """Return a paginated, optionally filtered list of accessible projects."""
    projects, total = await svc.list_for_user(
        db, current_user, pagination,
        status_filter=status_filter, domain=domain, search=search,
    )
    items = [ProjectList.model_validate(p) for p in projects]
    return PaginatedResponse.create(items, total, pagination.page, pagination.size)


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Get project detail",
)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    svc: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    """Retrieve a project by UUID. Respects visibility rules."""
    project = await svc.get_or_404(db, project_id, current_user)
    return ProjectRead.model_validate(project)


@router.patch(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Update project",
)
async def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    svc: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    """Partially update a project. Only the owner or an admin may do this."""
    project = await svc.update(db, project_id, payload, current_user)
    return ProjectRead.model_validate(project)


@router.delete(
    "/{project_id}",
    response_model=MessageResponse,
    summary="Archive (soft-delete) project",
)
async def delete_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    svc: ProjectService = Depends(get_project_service),
) -> MessageResponse:
    """Archive a project (sets status to ARCHIVED). Hard-delete is not exposed."""
    await svc.archive(db, project_id, current_user)
    return MessageResponse(message="Project archived.")


@router.post(
    "/{project_id}/publish",
    response_model=ProjectRead,
    summary="Publish project (set visibility to PUBLIC)",
)
async def publish_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    svc: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    """Set the project visibility to PUBLIC and status to ACTIVE."""
    project = await svc.publish(db, project_id, current_user)
    return ProjectRead.model_validate(project)
