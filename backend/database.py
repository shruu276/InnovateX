"""
database.py — SQLAlchemy async engine, session factories, Base model,
              and database dependency for FastAPI.

Public surface
--------------
    Base              — declarative base for all ORM models
    engine            — shared async engine (singleton)
    AsyncSessionLocal — async session factory
    SessionLocal      — sync session factory (Alembic / scripts)
    get_db            — FastAPI dependency (yields AsyncSession per request)
    connect_db()      — startup probe: verify DB is reachable
    disconnect_db()   — shutdown: dispose connection pool
    db_context()      — async context manager for use outside request scope
    check_db_health() — returns a DatabaseHealth dataclass with pool metrics
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import AsyncGenerator, Optional

import structlog
from sqlalchemy import NullPool, event, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool, NullPool as _NullPool, Pool

from config import settings

logger = structlog.get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Declarative Base
# ─────────────────────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Project-wide ORM base class.

    Every model must inherit from this class so that:
    - ``Base.metadata`` carries all table definitions for Alembic.
    - The shared engine/session factory can be applied to all models.

    Example::

        from database import Base

        class User(Base):
            __tablename__ = "users"
            id: Mapped[uuid.UUID] = mapped_column(primary_key=True, ...)
    """
    pass


# ─────────────────────────────────────────────────────────────────────────────
# Engine factory
# ─────────────────────────────────────────────────────────────────────────────
def _build_async_engine() -> AsyncEngine:
    """Construct the asyncpg-backed async engine from ``settings``.

    Pool strategy:
    - NullPool in test environments to avoid sharing connections across tests.
    - QueuePool (default) everywhere else for connection reuse.

    The ``connect_args`` block passes Postgres server parameters:
    - ``statement_timeout`` — hard-kill queries that run too long.
    - ``application_name``  — identifies this service in pg_stat_activity.
    """
    use_null_pool = settings.APP_ENV == "test"
    pool_class: type[Pool] = NullPool if use_null_pool else AsyncAdaptedQueuePool

    # NullPool does not accept pool sizing or timeout kwargs — build kwargs
    # conditionally so the same factory works in both test and production.
    pool_kwargs: dict = {"poolclass": pool_class, "pool_pre_ping": not use_null_pool}
    if not use_null_pool:
        pool_kwargs.update(
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_timeout=settings.DB_POOL_TIMEOUT,
        )

    engine = create_async_engine(
        settings.DATABASE_URL,
        # ── Logging ──────────────────────────────────────────────────────────
        echo=settings.db_echo,       # SQL statement logging (dev only)
        echo_pool=False,             # pool event logging (very noisy)
        # ── Pool ─────────────────────────────────────────────────────────────
        **pool_kwargs,
        # ── Postgres-specific ─────────────────────────────────────────────────
        connect_args={
            "server_settings": {
                "application_name": settings.APP_NAME,
                # Hard-kill any query exceeding the configured timeout.
                "statement_timeout": str(settings.DB_STATEMENT_TIMEOUT_MS),
                "lock_timeout":      "10000",   # 10 s lock-wait maximum
                "idle_in_transaction_session_timeout": "60000",  # 60 s
            },
            # asyncpg command_timeout is the network-level timeout (seconds)
            "command_timeout": 60,
        },
    )

    # Attach pool event listeners for observability
    _register_pool_events(engine)
    return engine


def _register_pool_events(engine: AsyncEngine) -> None:
    """Attach SQLAlchemy pool event listeners for structured logging."""

    @event.listens_for(engine.sync_engine, "connect")
    def on_connect(dbapi_conn, connection_record):  # noqa: ANN001
        logger.debug("db.pool.connect", pid=id(dbapi_conn))

    @event.listens_for(engine.sync_engine, "checkout")
    def on_checkout(dbapi_conn, connection_record, connection_proxy):  # noqa: ANN001
        logger.debug("db.pool.checkout", pool_size=engine.pool.size())

    @event.listens_for(engine.sync_engine, "checkin")
    def on_checkin(dbapi_conn, connection_record):  # noqa: ANN001
        logger.debug("db.pool.checkin")


# ─────────────────────────────────────────────────────────────────────────────
# Engine singleton  (module-level — built once on import)
# ─────────────────────────────────────────────────────────────────────────────
engine: AsyncEngine = _build_async_engine()


# ─────────────────────────────────────────────────────────────────────────────
# Session factories
# ─────────────────────────────────────────────────────────────────────────────
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,   # prevent lazy-load AttributeError after commit
)
"""Async session factory — use in FastAPI route handlers via ``get_db``."""

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine.sync_engine,
    autocommit=False,
    autoflush=False,
)
"""Synchronous session factory — use in Alembic data migrations and CLI scripts."""


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI dependency
# ─────────────────────────────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield one ``AsyncSession`` per HTTP request.

    Commits automatically on clean exit; rolls back on any exception.
    The session is always closed in the ``finally`` block.

    Usage::

        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as exc:
            await session.rollback()
            logger.error("db.session.rollback", error=str(exc))
            raise
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ─────────────────────────────────────────────────────────────────────────────
# Async context manager  (use outside request scope)
# ─────────────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def db_context() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager for background tasks, CLI scripts, and tests.

    Mirrors ``get_db`` semantics but works outside of FastAPI's DI system::

        async with db_context() as db:
            result = await db.execute(select(User))
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as exc:
            await session.rollback()
            logger.error("db.context.rollback", error=str(exc))
            raise
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ─────────────────────────────────────────────────────────────────────────────
# Health-check dataclass + probe
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class DatabaseHealth:
    """Snapshot of the database connection and pool state."""

    reachable: bool
    latency_ms: float
    pg_version: Optional[str]      = None
    pool_size: Optional[int]       = None
    checked_out: Optional[int]     = None
    overflow: Optional[int]        = None
    error: Optional[str]           = None

    @property
    def status(self) -> str:
        return "healthy" if self.reachable else "unhealthy"

    def as_dict(self) -> dict:
        return {
            "status":      self.status,
            "latency_ms":  round(self.latency_ms, 2),
            "pg_version":  self.pg_version,
            "pool": {
                "size":        self.pool_size,
                "checked_out": self.checked_out,
                "overflow":    self.overflow,
            },
            "error": self.error,
        }


async def check_db_health() -> DatabaseHealth:
    """Run a lightweight diagnostic against the database.

    Returns a ``DatabaseHealth`` snapshot — never raises.
    Called by the ``/health/ready`` readiness probe and the test script.
    """
    start = time.perf_counter()
    try:
        async with engine.connect() as conn:
            row = await conn.execute(
                text("SELECT version(), current_database(), pg_backend_pid()")
            )
            version, db_name, pid = row.one()
            latency_ms = (time.perf_counter() - start) * 1000

        pool = engine.pool
        health = DatabaseHealth(
            reachable=True,
            latency_ms=latency_ms,
            pg_version=version.split(" ")[1] if version else None,
            pool_size=pool.size(),
            checked_out=pool.checkedout(),
            overflow=pool.overflow(),
        )
        logger.info(
            "db.health.ok",
            db=db_name,
            pid=pid,
            latency_ms=round(latency_ms, 2),
        )
    except OperationalError as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        health = DatabaseHealth(
            reachable=False,
            latency_ms=latency_ms,
            error=str(exc.orig),
        )
        logger.error("db.health.fail", error=health.error)
    except Exception as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        health = DatabaseHealth(
            reachable=False,
            latency_ms=latency_ms,
            error=str(exc),
        )
        logger.error("db.health.fail", error=health.error)

    return health


# ─────────────────────────────────────────────────────────────────────────────
# Startup / shutdown hooks  (called from main.py lifespan)
# ─────────────────────────────────────────────────────────────────────────────
async def connect_db() -> None:
    """Verify the database is reachable at application startup.

    Raises on failure so the process exits instead of serving broken requests.
    """
    health = await check_db_health()
    if not health.reachable:
        raise RuntimeError(
            f"Cannot connect to PostgreSQL at startup: {health.error}"
        )
    logger.info(
        "database.connected",
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        db=settings.POSTGRES_DB,
        pg_version=health.pg_version,
        latency_ms=health.latency_ms,
    )


async def disconnect_db() -> None:
    """Dispose of the connection pool at application shutdown."""
    await engine.dispose(close=True)
    logger.info("database.disconnected")


# ─────────────────────────────────────────────────────────────────────────────
# Schema helpers  (used by test_db.py and integration tests)
# ─────────────────────────────────────────────────────────────────────────────
async def create_all_tables() -> None:
    """Create all tables defined on ``Base.metadata``.

    Only for development / test environments.  In production use Alembic.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database.tables_created")


async def drop_all_tables() -> None:
    """Drop all tables defined on ``Base.metadata``.

    Destructive — only call in test teardown or a full reset script.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.warning("database.tables_dropped")
