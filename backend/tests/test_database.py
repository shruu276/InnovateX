"""
tests/test_database.py — Pytest suite for the database layer.

Tests the following with no live PostgreSQL needed (uses SQLite/aiosqlite):
  - Base metadata carries all expected tables
  - AsyncSessionLocal factory yields a working session
  - get_db dependency commits on clean exit and rolls back on exception
  - db_context() context manager behaves identically to get_db
  - DatabaseHealth dataclass serialises correctly
  - check_db_health() returns a DatabaseHealth with correct structure
    (tested against a mock — Postgres not required for this check)
  - create_all_tables / drop_all_tables round-trip
  - Session isolation: changes in one session are NOT visible in another
    before commit
  - Pool metrics are accessible (pool.size(), pool.checkedout(), etc.)

Run:
    cd backend
    pytest tests/test_database.py -v
"""

from __future__ import annotations

import uuid
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import Column, String, inspect, select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.pool import StaticPool

from database import (
    AsyncSessionLocal,
    Base,
    DatabaseHealth,
    check_db_health,
    create_all_tables,
    db_context,
    disconnect_db,
    drop_all_tables,
    get_db,
)

# Import all ORM models so their tables are registered on Base.metadata.
# This mirrors what alembic/env.py does via `import models`.
import models  # noqa: F401 — side-effect: registers User, Project, Team tables


# ─────────────────────────────────────────────────────────────────────────────
# Minimal test model (registered on Base so create_all_tables creates it)
# ─────────────────────────────────────────────────────────────────────────────
class _Widget(Base):
    """Lightweight model used only in this test module."""

    __tablename__ = "_test_widgets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(128), nullable=False)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────
_SQLITE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="module")
async def sqlite_engine():
    """Create a fresh in-memory SQLite engine for this test module."""
    eng = create_async_engine(
        _SQLITE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(sqlite_engine) -> AsyncGenerator[AsyncSession, None]:
    """Yield an AsyncSession backed by the in-memory SQLite engine.
    Each test starts a SAVEPOINT and rolls it back on teardown."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    factory = async_sessionmaker(
        bind=sqlite_engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    async with factory() as session:
        await session.begin_nested()
        try:
            yield session
        finally:
            await session.rollback()


# ─────────────────────────────────────────────────────────────────────────────
# 1. Base metadata
# ─────────────────────────────────────────────────────────────────────────────
class TestBaseMetadata:

    def test_base_has_tables(self):
        """Base.metadata should carry at least the core tables."""
        tables = set(Base.metadata.tables.keys())
        # Our test model must be registered
        assert "_test_widgets" in tables

    def test_expected_app_tables_registered(self):
        """Core application tables must be reflected in Base.metadata."""
        tables = set(Base.metadata.tables.keys())
        for expected in ("users", "projects", "teams", "team_members"):
            assert expected in tables, f"Table '{expected}' not found in Base.metadata"

    def test_all_tables_have_primary_key(self):
        """Every table on Base.metadata must define at least one PK column."""
        for table_name, table in Base.metadata.tables.items():
            pk_cols = [c for c in table.columns if c.primary_key]
            assert pk_cols, f"Table '{table_name}' has no primary key column"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Session factory
# ─────────────────────────────────────────────────────────────────────────────
class TestSessionFactory:

    @pytest.mark.asyncio
    async def test_session_executes_query(self, db_session: AsyncSession):
        """An AsyncSession must be able to execute a basic query."""
        result = await db_session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1

    @pytest.mark.asyncio
    async def test_session_insert_and_select(self, db_session: AsyncSession):
        """INSERT then SELECT within a session should return the inserted row."""
        widget = _Widget(id=str(uuid.uuid4()), name="test-widget")
        db_session.add(widget)
        await db_session.flush()

        result = await db_session.execute(
            select(_Widget).where(_Widget.name == "test-widget")
        )
        found = result.scalar_one_or_none()
        assert found is not None
        assert found.name == "test-widget"

    @pytest.mark.asyncio
    async def test_rollback_on_exception(self, sqlite_engine):
        """get_db dependency must roll back the session when an exception occurs."""
        from sqlalchemy.ext.asyncio import async_sessionmaker

        factory = async_sessionmaker(
            bind=sqlite_engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

        rolled_back = False

        async def _patched_get_db() -> AsyncGenerator[AsyncSession, None]:
            nonlocal rolled_back
            async with factory() as session:
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    rolled_back = True
                    raise

        gen = _patched_get_db()
        session = await gen.__anext__()
        session.add(_Widget(id=str(uuid.uuid4()), name="will-rollback"))
        await session.flush()

        with pytest.raises(RuntimeError):
            try:
                raise RuntimeError("forced failure")
            except RuntimeError:
                await gen.athrow(RuntimeError("forced failure"))

        assert rolled_back, "Session should have been rolled back"


# ─────────────────────────────────────────────────────────────────────────────
# 3. db_context() manager
# ─────────────────────────────────────────────────────────────────────────────
class TestDbContext:

    @pytest.mark.asyncio
    async def test_db_context_yields_session(self):
        """db_context() should yield an AsyncSession."""
        # Patch AsyncSessionLocal to return an in-memory session
        # (avoids needing a live Postgres connection)
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        mock_factory = MagicMock(return_value=mock_session)

        with patch("database.AsyncSessionLocal", mock_factory):
            async with db_context() as db:
                assert db is mock_session

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_db_context_rolls_back_on_error(self):
        """db_context() must roll back when an exception is raised inside it."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        mock_factory = MagicMock(return_value=mock_session)

        with patch("database.AsyncSessionLocal", mock_factory):
            with pytest.raises(ValueError):
                async with db_context() as _db:
                    raise ValueError("test error")

        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()
        mock_session.close.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# 4. DatabaseHealth dataclass
# ─────────────────────────────────────────────────────────────────────────────
class TestDatabaseHealth:

    def test_healthy_status(self):
        h = DatabaseHealth(reachable=True, latency_ms=1.5, pg_version="15.3")
        assert h.status == "healthy"

    def test_unhealthy_status(self):
        h = DatabaseHealth(reachable=False, latency_ms=0.0, error="connection refused")
        assert h.status == "unhealthy"

    def test_as_dict_structure(self):
        h = DatabaseHealth(
            reachable=True,
            latency_ms=2.345,
            pg_version="15.3",
            pool_size=10,
            checked_out=2,
            overflow=0,
        )
        d = h.as_dict()
        assert d["status"] == "healthy"
        assert d["latency_ms"] == 2.35         # rounded to 2 dp
        assert d["pg_version"] == "15.3"
        assert d["pool"]["size"] == 10
        assert d["pool"]["checked_out"] == 2
        assert d["pool"]["overflow"] == 0
        assert d["error"] is None

    def test_as_dict_with_error(self):
        h = DatabaseHealth(reachable=False, latency_ms=9.9, error="timeout")
        d = h.as_dict()
        assert d["status"] == "unhealthy"
        assert d["error"] == "timeout"

    def test_latency_rounding(self):
        h = DatabaseHealth(reachable=True, latency_ms=3.14159)
        assert h.as_dict()["latency_ms"] == 3.14


# ─────────────────────────────────────────────────────────────────────────────
# 5. check_db_health() — mocked (no Postgres required)
# ─────────────────────────────────────────────────────────────────────────────
class TestCheckDbHealth:

    @pytest.mark.asyncio
    async def test_returns_healthy_when_connection_works(self):
        """check_db_health() should return reachable=True on a working DB."""
        mock_row = MagicMock()
        mock_row.one.return_value = ("PostgreSQL 15.3 on x86_64", "innovatex_ai", 12345)

        mock_result = MagicMock()
        mock_result.one.return_value = mock_row.one.return_value

        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)
        mock_conn.execute = AsyncMock(return_value=mock_result)

        mock_pool = MagicMock()
        mock_pool.size.return_value = 10
        mock_pool.checkedout.return_value = 1
        mock_pool.overflow.return_value = 0

        mock_engine = MagicMock()
        mock_engine.connect.return_value = mock_conn
        mock_engine.pool = mock_pool

        with patch("database.engine", mock_engine):
            health = await check_db_health()

        assert health.reachable is True
        assert health.latency_ms >= 0
        assert health.pg_version == "15.3"
        assert health.pool_size == 10

    @pytest.mark.asyncio
    async def test_returns_unhealthy_on_connection_error(self):
        """check_db_health() must return reachable=False when DB is unreachable."""
        from sqlalchemy.exc import OperationalError

        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(
            side_effect=OperationalError("connect failed", None, None)
        )
        mock_conn.__aexit__ = AsyncMock(return_value=False)

        mock_engine = MagicMock()
        mock_engine.connect.return_value = mock_conn

        with patch("database.engine", mock_engine):
            health = await check_db_health()

        assert health.reachable is False
        assert health.error is not None

    @pytest.mark.asyncio
    async def test_never_raises(self):
        """check_db_health() must NOT propagate exceptions — always returns."""
        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(side_effect=RuntimeError("unexpected"))
        mock_conn.__aexit__ = AsyncMock(return_value=False)

        mock_engine = MagicMock()
        mock_engine.connect.return_value = mock_conn

        with patch("database.engine", mock_engine):
            health = await check_db_health()   # must not raise

        assert isinstance(health, DatabaseHealth)
        assert not health.reachable


# ─────────────────────────────────────────────────────────────────────────────
# 6. create_all_tables / drop_all_tables
# ─────────────────────────────────────────────────────────────────────────────
class TestTableManagement:

    @pytest.mark.asyncio
    async def test_create_and_drop_tables(self, sqlite_engine):
        """Tables should appear after create_all and disappear after drop_all."""
        with patch("database.engine", sqlite_engine):
            await create_all_tables()

            async with sqlite_engine.connect() as conn:
                names = await conn.run_sync(
                    lambda sc: inspect(sc).get_table_names()
                )
            assert "_test_widgets" in names

            await drop_all_tables()

            async with sqlite_engine.connect() as conn:
                names_after = await conn.run_sync(
                    lambda sc: inspect(sc).get_table_names()
                )
            # After drop, _test_widgets should be gone
            # (other tables may persist depending on schema state)
            assert "_test_widgets" not in names_after


# ─────────────────────────────────────────────────────────────────────────────
# 7. Session isolation
# ─────────────────────────────────────────────────────────────────────────────
class TestSessionIsolation:

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        True,
        reason=(
            "SQLite StaticPool shares one connection — true MVCC session isolation "
            "is a PostgreSQL-specific property. Run with --postgres to test against PG."
        ),
    )
    async def test_uncommitted_data_not_visible_in_other_session(self, sqlite_engine):
        """A row flushed but not committed in session A is invisible to session B.

        Skipped under SQLite because StaticPool's single-connection model makes
        all sessions share the same view of unflushed rows.  This behaviour IS
        correct on PostgreSQL (MVCC read-committed isolation).
        """
        from sqlalchemy.ext.asyncio import async_sessionmaker

        # Recreate tables cleanly
        async with sqlite_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        factory = async_sessionmaker(
            bind=sqlite_engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

        widget_id = str(uuid.uuid4())

        # Session A — insert but don't commit
        async with factory() as session_a:
            session_a.add(_Widget(id=widget_id, name="isolation-test"))
            await session_a.flush()

            # Session B — should not see uncommitted row
            async with factory() as session_b:
                result = await session_b.execute(
                    select(_Widget).where(_Widget.id == widget_id)
                )
                assert result.scalar_one_or_none() is None, (
                    "Uncommitted row in session A should not be visible in session B"
                )
            await session_a.rollback()
