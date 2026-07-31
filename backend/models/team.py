"""
models/team.py — Team and TeamMember ORM models.

A Team groups one or more Users around a set of Projects. A User can
belong to multiple teams with different roles in each (OWNER, ADMIN, MEMBER).
"""

from __future__ import annotations

import uuid
import enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from models.base import TimestampMixin

if TYPE_CHECKING:
    from models.user import User
    from models.project import Project


class TeamRole(str, enum.Enum):
    """Role of a user within a specific team."""
    OWNER  = "owner"    # created the team; full control
    ADMIN  = "admin"    # can invite / remove members and edit projects
    MEMBER = "member"   # standard collaborator
    VIEWER = "viewer"   # read-only access (stakeholder / sponsor)


class Team(TimestampMixin, Base):
    """A named group of users collaborating on projects."""

    __tablename__ = "teams"
    __table_args__ = {"comment": "Collaborative teams on the platform"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(256), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    institution: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    members: Mapped[List["TeamMember"]] = relationship(
        "TeamMember",
        back_populates="team",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="team",
        lazy="noload",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Team id={self.id!s:.8} slug={self.slug}>"


class TeamMember(TimestampMixin, Base):
    """Association table between Users and Teams, carrying the member's role."""

    __tablename__ = "team_members"
    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uq_team_member"),
        {"comment": "Maps users to teams with their respective roles"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[TeamRole] = mapped_column(
        Enum(TeamRole, name="team_role_enum"),
        nullable=False,
        default=TeamRole.MEMBER,
    )
    invited_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    team: Mapped["Team"] = relationship("Team", back_populates="members", lazy="noload")
    user: Mapped["User"] = relationship("User", back_populates="team_memberships",
                                        foreign_keys=[user_id], lazy="noload")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<TeamMember team={self.team_id!s:.8} user={self.user_id!s:.8} role={self.role}>"
