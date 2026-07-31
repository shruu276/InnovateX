"""
models/user.py — User ORM model.

Represents any registered account regardless of their sector role (student,
researcher, industry partner, government official, mentor, admin).
"""

from __future__ import annotations

import uuid
import enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Enum, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from models.base import TimestampMixin

if TYPE_CHECKING:
    from models.project import Project
    from models.team import Team, TeamMember


class UserRole(str, enum.Enum):
    """High-level role assigned at registration. Controls which dashboard
    and feature set the user sees."""
    STUDENT        = "student"
    RESEARCHER     = "researcher"
    FACULTY        = "faculty"
    INDUSTRY       = "industry"
    STARTUP        = "startup"
    GOVERNMENT     = "government"
    MENTOR         = "mentor"
    ADMIN          = "admin"


class UserStatus(str, enum.Enum):
    """Lifecycle state of the account."""
    PENDING    = "pending"    # registered but not yet email-verified
    ACTIVE     = "active"     # fully operational account
    SUSPENDED  = "suspended"  # admin-imposed temporary ban
    DEACTIVATED = "deactivated"  # user-initiated soft delete


class User(TimestampMixin, Base):
    """Core user table."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        {"comment": "Registered InnovateX AI users"},
    )

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Surrogate primary key (UUID v4).",
    )
    email: Mapped[str] = mapped_column(
        String(320),   # RFC 5321 max length
        nullable=False,
        index=True,
        doc="User's email address — used as login credential.",
    )
    hashed_password: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        doc="bcrypt hash of the user's password.",
    )

    # ── Profile ───────────────────────────────────────────────────────────────
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str]  = mapped_column(String(100), nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    institution: Mapped[Optional[str]] = mapped_column(String(256), nullable=True,
        doc="University, company, or agency name.")
    department: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    # ── Role & status ─────────────────────────────────────────────────────────
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role_enum"),
        nullable=False,
        default=UserRole.STUDENT,
        index=True,
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status_enum"),
        nullable=False,
        default=UserStatus.PENDING,
        index=True,
    )

    # ── Auth flags ────────────────────────────────────────────────────────────
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_verified: Mapped[bool]  = mapped_column(Boolean, nullable=False, default=False,
        doc="True once the user has clicked the email-verification link.")
    is_mfa_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mfa_secret: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # ── Innovation score ──────────────────────────────────────────────────────
    innovation_score: Mapped[int] = mapped_column(
        nullable=False, default=0,
        doc="Composite gamified score derived from project activity.",
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    # projects this user owns
    owned_projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    # team memberships
    team_memberships: Mapped[List["TeamMember"]] = relationship(
        "TeamMember",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="noload",
    )

    # ── Helpers ───────────────────────────────────────────────────────────────
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id!s:.8} email={self.email}>"
