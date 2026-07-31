"""
utils/pagination.py — Standard pagination query-parameter dependency.

Usage in a route::

    from utils.pagination import PaginationParams

    @router.get("/items")
    async def list_items(pagination: PaginationParams = Depends()):
        offset = pagination.offset
        limit  = pagination.size
        ...
"""

from __future__ import annotations

from fastapi import Query
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Query parameter bag for paginated list endpoints.

    Injected as a FastAPI dependency::

        async def handler(p: PaginationParams = Depends()):

    Attributes:
        page:   1-based page number (default: 1).
        size:   Items per page (default: 20, max: 100).
        offset: Computed byte-offset for SQL OFFSET clause.
    """

    page: int = Field(Query(default=1, ge=1, description="Page number (1-based)"))
    size: int = Field(Query(default=20, ge=1, le=100, description="Items per page"))

    @property
    def offset(self) -> int:
        """Return the SQL OFFSET value for the current page."""
        return (self.page - 1) * self.size

    class Config:
        # Allow FastAPI to populate fields from query parameters
        arbitrary_types_allowed = True
