"""
tests/conftest.py — Shared pytest fixtures for the backend test suite.

Provides:
    async_engine   — in-process async SQLite engine (no Postgres needed)
    async_session  — isolated AsyncSession per test (rolled back after each)
    sync_engine    — synchronous SQLite engine for schema introspection
    override_db    — patches FastAPI's get_db dependency in integration tests

The SQLite engine uses the ``aiosqlite`` driver so async tests work without
a live PostgreSQL instance.  Tests that explicitly need Postgres should be
marked with ``@pytest.mark.postgres`` and skipped in CI unless a real DB
is configured.

Setup:
    pip install pytest pytest-asyncio aiosqlite
"""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy import StaticPool, event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine

# ── Import app modules (backend/ must be on sys.path — set in pytest.ini / pyproject) ──
from database import Base, get_db
from config import settings


# ─────────────────────────────────────────────────────────────────────────────
# pytest-asyncio configuration
# ─────────────────────────────────────────────────────────────────────────────
# Use "auto" mode so every async test function is automatically treated as
# asyncio without needing @pytest.mark.asyncio on each one.

def pytest_configure(config):  # noqa: ANN001
    config.addinivalue_line(
        "markers",
        "postgres: mark test as requiring a live PostgreSQL instance",
    )


# ─────────────────────────────────────────────────────────────────────────────
# In-memory SQLite engine (no Postgres required)
# ─────────────────────────────────────────────────────────────────────────────
_SQLITE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Session-scoped in-memory SQLite async engine.

    Creates all tables on start; drops them at the end of the test session.
    Shared across all tests in the session to avoid the overhead of repeated
    schema creation.
    """
    engine = create_async_engine(
        _SQLITE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,     # single connection — required for :memory: SQLite
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Function-scoped AsyncSession wrapped in a SAVEPOINT.

    Every test gets a clean state because the SAVEPOINT is rolled back at the
    end of the test — no data from one test leaks into another.
    """
    factory = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    async with factory() as session:
        # Nest the entire test inside a SAVEPOINT so we can roll back
        await session.begin_nested()
        try:
            yield session
        finally:
            await session.rollback()
        await session.close()


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI dependency override
# ─────────────────────────────────────────────────────────────────────────────
@pytest_asyncio.fixture
async def override_db(
    async_session: AsyncSession,
) -> AsyncGenerator[AsyncSession, None]:
    """Override the FastAPI get_db dependency with the test session.

    Use in integration tests that spin up a TestClient::

        from fastapi.testclient import TestClient
        from main import app

        @pytest_asyncio.fixture
        async def client(override_db):
            app.dependency_overrides[get_db] = lambda: override_db
            yield TestClient(app)
            app.dependency_overrides.clear()
    """
    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield async_session

    from main import app
    app.dependency_overrides[get_db] = _get_test_db
    yield async_session
    app.dependency_overrides.clear()
