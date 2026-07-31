"""
routes/health.py — Liveness and readiness probe endpoints.

Used by Kubernetes / load balancers to check service availability.
"""

from __future__ import annotations

import time
from typing import Any, Dict

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db

router = APIRouter()

_start_time = time.time()


@router.get(
    "/health",
    summary="Liveness probe",
    description="Returns 200 when the application process is running.",
    response_class=ORJSONResponse,
    tags=["Health"],
)
async def liveness() -> Dict[str, Any]:
    """Lightweight check — no DB call.  Use for Kubernetes liveness probe."""
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - _start_time, 2),
    }


@router.get(
    "/health/ready",
    summary="Readiness probe",
    description="Returns 200 only when the database is reachable.",
    response_class=ORJSONResponse,
    tags=["Health"],
)
async def readiness(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Performs a lightweight DB ping. Use for Kubernetes readiness probe."""
    await db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": "reachable",
    }
