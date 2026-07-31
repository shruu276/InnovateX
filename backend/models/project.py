"""
models/project.py — Project ORM model.

A Project is the central entity. It has an owner, belongs to one or more
teams, and can have an arbitrary number of tasks and milestones (modelled
in future migration files).
"""

from __future__ import annotations

import uuid
import enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    ARRAY, Boolean, Enum, ForeignKey, Integer, String, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from models.base import TimestampMixin

if TYPE_CHECKING:
    from models.user import User
    from models.team import Team


class ProjectStatus(str, enum.Enum):
    """Where the project is in its lifecycle."""
    DRAFT       = "draft"
    ACTIVE      = "active"
    ON_HOLD     = "on_hold"
    COMPLETED   = "completed"
    ARCHIVED    = "archived"
    CANCELLED   = "cancelled"


class ProjectVisibility(str, enum.Enum):
    """Who can discover and read the project."""
    PRIVATE  = "private"   # owner + explicit members only
    TEAM     = "team"      # all team members
    PUBLIC   = "public"    # anyone on the platform can view


class Project(TimestampMixin, Base):
    """Core project entity."""

    __tablename__ = "projects"
    __table_args__ = {"comment": "Innovation projects on the platform"}

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    slug: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        unique=True,
        index=True,
        doc="URL-friendly identifier (e.g. 'climate-tech-carbon-capture').",
    )

    # ── Content ───────────────────────────────────────────────────────────────
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    tagline: Mapped[Optional[str]] = mapped_column(String(512), nullable=True,
        doc="One-line summary shown in project cards.")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True,
        doc="Full markdown-supported description.")
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    # ── Classification ────────────────────────────────────────────────────────
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status_enum"),
        nullable=False,
        default=ProjectStatus.DRAFT,
        index=True,
    )
    visibility: Mapped[ProjectVisibility] = mapped_column(
        Enum(ProjectVisibility, name="project_visibility_enum"),
        nullable=False,
        default=ProjectVisibility.PRIVATE,
    )
    domain: Mapped[Optional[str]] = mapped_column(String(128), nullable=True,
        doc="Research / industry domain (e.g. 'climate-tech', 'biomedical').")
    # Tags stored as a PostgreSQL text array for simple querying
    tags: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(64)),
        nullable=True,
        default=list,
    )

    # ── Metrics ───────────────────────────────────────────────────────────────
    innovation_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    view_count: Mapped[int]       = mapped_column(Integer, nullable=False, default=0)
    like_count: Mapped[int]       = mapped_column(Integer, nullable=False, default=0)

    # ── Funding ───────────────────────────────────────────────────────────────
    funding_goal: Mapped[Optional[int]] = mapped_column(Integer, nullable=True,
        doc="Target funding amount in USD cents.")
    funding_raised: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_seeking_funding: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_seeking_collaborators: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # ── Foreign keys ──────────────────────────────────────────────────────────
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    team_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="owned_projects",
        lazy="noload",
    )
    team: Mapped[Optional["Team"]] = relationship(
        "Team",
        back_populates="projects",
        lazy="noload",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Project id={self.id!s:.8} slug={self.slug}>"
