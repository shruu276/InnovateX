"""
schemas/common.py — Shared Pydantic schema primitives.

These are used as response envelopes and utility types throughout the API.
"""

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

DataT = TypeVar("DataT")


class BaseSchema(BaseModel):
    """Root schema from which all project schemas derive.

    - `from_attributes=True`  → allows constructing from ORM model instances
    - `populate_by_name=True` → allows using both field name and alias
    """
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class MessageResponse(BaseSchema):
    """Generic envelope for endpoints that return only a status message."""
    success: bool = True
    message: str

    model_config = ConfigDict(
        json_schema_extra={"example": {"success": True, "message": "Operation completed."}}
    )


class PaginatedResponse(BaseSchema, Generic[DataT]):
    """Standard envelope for paginated list endpoints.

    Usage::

        @router.get("/", response_model=PaginatedResponse[ProjectRead])
        async def list_projects(...):
    """
    items: List[DataT]
    total: int = Field(..., description="Total number of matching records")
    page: int  = Field(..., ge=1, description="Current page number (1-based)")
    size: int  = Field(..., ge=1, le=100, description="Items per page")
    pages: int = Field(..., description="Total number of pages")

    @classmethod
    def create(
        cls,
        items: List[DataT],
        total: int,
        page: int,
        size: int,
    ) -> "PaginatedResponse[DataT]":
        pages = max(1, (total + size - 1) // size)
        return cls(items=items, total=total, page=page, size=size, pages=pages)
