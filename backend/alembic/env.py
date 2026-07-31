"""
alembic/env.py — Alembic migration environment.

This file is executed by Alembic for every migration command.
It configures the database URL and imports all ORM models so
autogenerate can detect schema changes.

Online mode  (default): connects to a live DB to apply migrations.
Offline mode (--sql):   generates plain SQL scripts without connecting.
"""

from __future__ import annotations

import sys
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# ── Make the backend package importable ───────────────────────────────────────
# When running `alembic` from the backend/ directory, this is usually not
# needed. But when running from the repo root it ensures imports resolve.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Import application settings and models ────────────────────────────────────
from config import settings   # noqa: E402 — must be after sys.path insert
from database import Base     # noqa: E402

# Import ALL models so their tables are registered on Base.metadata.
# Alembic uses Base.metadata to detect schema changes during autogenerate.
import models  # noqa: F401, E402 — side-effect import

# ── Alembic Config object ─────────────────────────────────────────────────────
config = context.config

# Override the sqlalchemy.url from alembic.ini with the real value from
# our application settings (which reads from .env).
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL_SYNC)

# ── Logging ───────────────────────────────────────────────────────────────────
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Target metadata ───────────────────────────────────────────────────────────
# This tells autogenerate which tables to compare the DB against.
target_metadata = Base.metadata


# ── Helper: include / exclude tables ─────────────────────────────────────────
def include_object(object, name, type_, reflected, compare_to):
    """Return False for objects that should be excluded from autogenerate.

    Add PostGIS geography columns, third-party extension tables, etc. here.
    """
    return True


# ── Offline mode ─────────────────────────────────────────────────────────────
def run_migrations_offline() -> None:
    """Emit migration SQL to stdout without a live database connection.

    Usage:
        alembic upgrade head --sql > migrations.sql
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        compare_type=True,      # detect column type changes
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online mode ───────────────────────────────────────────────────────────────
def run_migrations_online() -> None:
    """Connect to the database and apply migrations directly."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,   # don't pool connections in migration scripts
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


# ── Entrypoint ────────────────────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
