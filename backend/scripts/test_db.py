#!/usr/bin/env python
"""
scripts/test_db.py — Standalone PostgreSQL connection diagnostic.

Runs a comprehensive set of checks against the database configured in .env
and prints a colour-coded report to stdout.  Exits 0 on success, 1 on any
failure.

Usage (from the backend/ directory):
    python scripts/test_db.py
    python scripts/test_db.py --verbose
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from textwrap import indent
from typing import List, Tuple

# Ensure backend/ is on sys.path when run from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession

# ── Import after path fix ─────────────────────────────────────────────────────
from config import settings
from database import (
    AsyncSessionLocal,
    Base,
    check_db_health,
    create_all_tables,
    db_context,
    disconnect_db,
    drop_all_tables,
    engine,
)

# ── Console colours (auto-disabled when stdout is not a TTY) ─────────────────
_IS_TTY = sys.stdout.isatty()


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _IS_TTY else text


OK   = _c("✓", "32;1")
FAIL = _c("✗", "31;1")
WARN = _c("!", "33;1")
INFO = _c("→", "36")
HEAD = lambda t: _c(t, "1")          # bold


# ─────────────────────────────────────────────────────────────────────────────
# Individual check functions
# ─────────────────────────────────────────────────────────────────────────────
async def check_01_basic_ping() -> Tuple[bool, str]:
    """Open one connection and execute SELECT 1."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True, "SELECT 1 returned successfully."
    except Exception as exc:
        return False, str(exc)


async def check_02_health_probe() -> Tuple[bool, str]:
    """Invoke check_db_health() and inspect the result."""
    health = await check_db_health()
    detail = json.dumps(health.as_dict(), indent=2)
    return health.reachable, detail


async def check_03_database_exists() -> Tuple[bool, str]:
    """Confirm the target database name matches settings."""
    try:
        async with engine.connect() as conn:
            row = await conn.execute(text("SELECT current_database()"))
            db_name = row.scalar_one()
        match = db_name == settings.POSTGRES_DB
        msg = (
            f"Connected to database '{db_name}'."
            if match
            else f"Connected to '{db_name}' but settings.POSTGRES_DB='{settings.POSTGRES_DB}'."
        )
        return match, msg
    except Exception as exc:
        return False, str(exc)


async def check_04_pg_version() -> Tuple[bool, str]:
    """Read the PostgreSQL server version and assert >= 14."""
    try:
        async with engine.connect() as conn:
            row = await conn.execute(text("SHOW server_version"))
            version_str: str = row.scalar_one()
        major = int(version_str.split(".")[0])
        ok = major >= 14
        return ok, f"PostgreSQL {version_str} (minimum required: 14)."
    except Exception as exc:
        return False, str(exc)


async def check_05_session_factory() -> Tuple[bool, str]:
    """Obtain a session via AsyncSessionLocal and run a query."""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT pg_backend_pid()"))
            pid = result.scalar_one()
        return True, f"AsyncSession acquired (backend PID {pid})."
    except Exception as exc:
        return False, str(exc)


async def check_06_db_context() -> Tuple[bool, str]:
    """Use the db_context() async context manager."""
    try:
        async with db_context() as db:
            result = await db.execute(
                text("SELECT current_timestamp AT TIME ZONE 'UTC'")
            )
            ts = result.scalar_one()
        return True, f"db_context() OK — server UTC time: {ts}."
    except Exception as exc:
        return False, str(exc)


async def check_07_extensions() -> Tuple[bool, str]:
    """Check for recommended PostgreSQL extensions."""
    RECOMMENDED = ["uuid-ossp", "pgcrypto"]
    try:
        async with engine.connect() as conn:
            rows = await conn.execute(
                text("SELECT extname FROM pg_extension ORDER BY extname")
            )
            installed = {r[0] for r in rows.fetchall()}
        missing = [e for e in RECOMMENDED if e not in installed]
        if missing:
            return (
                True,   # not a hard failure
                f"Installed: {sorted(installed)}. "
                f"Recommended but missing: {missing} — "
                f"run CREATE EXTENSION IF NOT EXISTS \"<name>\" to install.",
            )
        return True, f"All recommended extensions present: {RECOMMENDED}."
    except Exception as exc:
        return False, str(exc)


async def check_08_table_creation() -> Tuple[bool, str]:
    """Create all tables on Base.metadata in a temp schema and drop them."""
    try:
        await create_all_tables()
        # Inspect via sync inspection inside a run_sync call
        async with engine.connect() as conn:
            table_names = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).get_table_names()
            )
        expected = set(Base.metadata.tables.keys())
        created  = set(table_names)
        missing  = expected - created

        # Tear down immediately
        await drop_all_tables()

        if missing:
            return False, f"Expected tables not created: {missing}."
        return True, f"Created and dropped {len(expected)} tables: {sorted(expected)}."
    except Exception as exc:
        return False, str(exc)


async def check_09_read_write_transaction() -> Tuple[bool, str]:
    """Execute an INSERT + SELECT + DELETE inside a real transaction."""
    try:
        async with engine.begin() as conn:
            # Use a temp table to avoid polluting real schema
            await conn.execute(text(
                "CREATE TEMP TABLE _rw_test (id serial PRIMARY KEY, val text NOT NULL)"
            ))
            await conn.execute(text(
                "INSERT INTO _rw_test (val) VALUES (:v)"
            ), {"v": "innovatex_ai_probe"})
            row = await conn.execute(text("SELECT val FROM _rw_test LIMIT 1"))
            val = row.scalar_one()
            await conn.execute(text("DROP TABLE _rw_test"))

        ok = val == "innovatex_ai_probe"
        return ok, f"INSERT / SELECT / DELETE cycle OK (got '{val}')."
    except Exception as exc:
        return False, str(exc)


async def check_10_pool_metrics() -> Tuple[bool, str]:
    """Report connection pool statistics."""
    try:
        pool = engine.pool
        msg = (
            f"Pool size: {pool.size()}, "
            f"checked out: {pool.checkedout()}, "
            f"overflow: {pool.overflow()}, "
            f"invalid: {pool.invalidated()}."
        )
        return True, msg
    except Exception as exc:
        return False, str(exc)


# ─────────────────────────────────────────────────────────────────────────────
# Check registry
# ─────────────────────────────────────────────────────────────────────────────
CHECKS = [
    ("01 — Basic ping (SELECT 1)",          check_01_basic_ping),
    ("02 — Health-probe dataclass",         check_02_health_probe),
    ("03 — Database name matches .env",     check_03_database_exists),
    ("04 — PostgreSQL version ≥ 14",        check_04_pg_version),
    ("05 — AsyncSessionLocal factory",      check_05_session_factory),
    ("06 — db_context() manager",           check_06_db_context),
    ("07 — Recommended extensions",         check_07_extensions),
    ("08 — ORM table create / drop",        check_08_table_creation),
    ("09 — Read / write transaction",       check_09_read_write_transaction),
    ("10 — Connection pool metrics",        check_10_pool_metrics),
]


# ─────────────────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────────────────
async def run_checks(verbose: bool = False) -> int:
    """Run all checks and print a formatted report.  Returns exit code."""
    width = 60

    print()
    print(HEAD("=" * width))
    print(HEAD("  InnovateX AI — PostgreSQL Connection Diagnostic"))
    print(HEAD("=" * width))
    print(f"  {INFO} Host      : {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
    print(f"  {INFO} Database  : {settings.POSTGRES_DB}")
    print(f"  {INFO} User      : {settings.POSTGRES_USER}")
    print(f"  {INFO} Pool size : {settings.DB_POOL_SIZE} + {settings.DB_MAX_OVERFLOW} overflow")
    print(HEAD("-" * width))
    print()

    results: List[Tuple[str, bool, str, float]] = []
    failed = 0

    for name, fn in CHECKS:
        t0 = time.perf_counter()
        try:
            ok, detail = await fn()
        except Exception as exc:
            ok, detail = False, f"Unexpected exception: {exc}"
        elapsed_ms = (time.perf_counter() - t0) * 1000

        icon = OK if ok else FAIL
        status_label = _c("PASS", "32") if ok else _c("FAIL", "31;1")
        print(f"  {icon}  {name:<42}  {status_label}  ({elapsed_ms:>6.1f} ms)")

        if verbose or not ok:
            print(indent(detail, "       "))
            print()

        results.append((name, ok, detail, elapsed_ms))
        if not ok:
            failed += 1

    print()
    print(HEAD("-" * width))
    total   = len(results)
    passed  = total - failed
    summary = (
        _c(f"  {passed}/{total} checks passed.", "32;1")
        if failed == 0
        else _c(f"  {passed}/{total} passed — {failed} FAILED.", "31;1")
    )
    print(summary)
    print(HEAD("=" * width))
    print()

    await disconnect_db()
    return 0 if failed == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Test the InnovateX AI PostgreSQL connection."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detail output for every check, not just failures.",
    )
    args = parser.parse_args()
    exit_code = asyncio.run(run_checks(verbose=args.verbose))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
