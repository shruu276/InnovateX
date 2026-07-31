"""
models/base.py — Shared mixins for all ORM models.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Adds created_at and updated_at columns to any model that inherits it.

    SQLAlchemy handles updated_at via the onupdate hook so application code
    never has to touch it manually.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        doc="UTC timestamp when the row was first inserted.",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=_utcnow,
        nullable=False,
        doc="UTC timestamp of the last UPDATE on this row.",
    )
