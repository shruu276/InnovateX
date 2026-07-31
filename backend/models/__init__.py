"""
models/__init__.py

Re-export all ORM models so Alembic's env.py can import them from one place:

    from models import Base, User, Project, Team, ...

This ensures all tables are registered on Base.metadata before
`alembic.env` calls `Base.metadata.create_all()`.
"""

from models.base import TimestampMixin
from models.user import User, UserRole, UserStatus
from models.project import Project, ProjectStatus, ProjectVisibility
from models.team import Team, TeamMember, TeamRole
from database import Base

__all__ = [
    "Base",
    # Mixins
    "TimestampMixin",
    # User
    "User",
    "UserRole",
    "UserStatus",
    # Project
    "Project",
    "ProjectStatus",
    "ProjectVisibility",
    # Team
    "Team",
    "TeamMember",
    "TeamRole",
]
