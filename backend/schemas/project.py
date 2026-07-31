"""
schemas/project.py — Project request / response Pydantic schemas.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from pydantic import Field, field_validator

from models.project import ProjectStatus, ProjectVisibility
from schemas.common import BaseSchema
from schemas.user import UserReadPublic


# ── Create ────────────────────────────────────────────────────────────────────
class ProjectCreate(BaseSchema):
    """Request body for POST /projects."""
    title: str       = Field(..., min_length=3, max_length=256)
    tagline: Optional[str] = Field(None, max_length=512)
    description: Optional[str] = None
    visibility: ProjectVisibility = ProjectVisibility.PRIVATE
    domain: Optional[str] = Field(None, max_length=128)
    tags: Optional[List[str]] = Field(default_factory=list, max_length=20)
    is_seeking_funding: bool = False
    is_seeking_collaborators: bool = True

    @field_validator("tags")
    @classmethod
    def limit_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v and len(v) > 20:
            raise ValueError("Maximum of 20 tags allowed.")
        return v


# ── Update ────────────────────────────────────────────────────────────────────
class ProjectUpdate(BaseSchema):
    """Request body for PATCH /projects/{id} — all fields optional."""
    title: Optional[str]             = Field(None, min_length=3, max_length=256)
    tagline: Optional[str]           = Field(None, max_length=512)
    description: Optional[str]       = None
    visibility: Optional[ProjectVisibility] = None
    status: Optional[ProjectStatus]  = None
    domain: Optional[str]            = Field(None, max_length=128)
    tags: Optional[List[str]]        = None
    cover_image_url: Optional[str]   = Field(None, max_length=1024)
    is_seeking_funding: Optional[bool] = None
    is_seeking_collaborators: Optional[bool] = None
    funding_goal: Optional[int]      = Field(None, ge=0,
        description="Funding goal in USD cents.")


# ── Read (full — team members / owner) ───────────────────────────────────────
class ProjectRead(BaseSchema):
    """Full project detail returned to team members."""
    id: uuid.UUID
    slug: str
    title: str
    tagline: Optional[str]
    description: Optional[str]
    cover_image_url: Optional[str]
    status: ProjectStatus
    visibility: ProjectVisibility
    domain: Optional[str]
    tags: Optional[List[str]]
    innovation_score: int
    view_count: int
    like_count: int
    funding_goal: Optional[int]
    funding_raised: int
    is_seeking_funding: bool
    is_seeking_collaborators: bool
    owner_id: uuid.UUID
    team_id: Optional[uuid.UUID]
    owner: Optional[UserReadPublic] = None


# ── Read (public — discovery) ─────────────────────────────────────────────────
class ProjectReadPublic(BaseSchema):
    """Stripped project returned in public discovery / search results."""
    id: uuid.UUID
    slug: str
    title: str
    tagline: Optional[str]
    cover_image_url: Optional[str]
    status: ProjectStatus
    domain: Optional[str]
    tags: Optional[List[str]]
    innovation_score: int
    like_count: int
    is_seeking_funding: bool
    is_seeking_collaborators: bool
    owner: Optional[UserReadPublic] = None


# ── List item ─────────────────────────────────────────────────────────────────
class ProjectList(BaseSchema):
    """Compact row used in paginated project listings."""
    id: uuid.UUID
    slug: str
    title: str
    tagline: Optional[str]
    status: ProjectStatus
    visibility: ProjectVisibility
    domain: Optional[str]
    tags: Optional[List[str]]
    innovation_score: int
