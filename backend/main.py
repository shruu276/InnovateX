"""
main.py — FastAPI application factory and entry point.

Run locally:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Production (gunicorn + uvicorn workers):
    gunicorn main:app -k uvicorn.workers.UvicornWorker -w 4
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import settings
from database import connect_db, disconnect_db
from routes import auth, health, projects, users

logger = structlog.get_logger(__name__)


# ── Lifespan (replaces on_event deprecated in FastAPI 0.93+) ─────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage startup and shutdown side-effects."""
    # ── Startup ──────────────────────────────────────────────────────────────
    logger.info("app.startup", name=settings.APP_NAME, version=settings.APP_VERSION, env=settings.APP_ENV)
    await connect_db()

    yield   # ← application runs here

    # ── Shutdown ─────────────────────────────────────────────────────────────
    await disconnect_db()
    logger.info("app.shutdown")


# ── Application factory ───────────────────────────────────────────────────────
def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""

    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "InnovateX AI — API for bridging Academia, Industry, "
            "Government & Startups through AI-assisted collaboration."
        ),
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        default_response_class=ORJSONResponse,   # faster JSON serialisation
        lifespan=lifespan,
    )

    # ── Middleware (order matters — outermost = first to receive request) ──────
    _register_middleware(application)

    # ── Exception handlers ────────────────────────────────────────────────────
    _register_exception_handlers(application)

    # ── Routers ───────────────────────────────────────────────────────────────
    _register_routers(application)

    return application


def _register_middleware(app: FastAPI) -> None:
    """Attach all middleware to the application."""

    # GZip — compress responses larger than 1 KB
    app.add_middleware(GZipMiddleware, minimum_size=1024)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
    )

    # Request-ID + timing — custom middleware via decorator
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        """Attach X-Process-Time and X-Request-ID response headers."""
        import uuid
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start = time.perf_counter()

        # Bind request context to all logs within this request
        with structlog.contextvars.bound_contextvars(request_id=request_id, path=request.url.path):
            response = await call_next(request)

        elapsed = (time.perf_counter() - start) * 1000
        response.headers["X-Process-Time"] = f"{elapsed:.2f}ms"
        response.headers["X-Request-ID"] = request_id
        return response


def _register_exception_handlers(app: FastAPI) -> None:
    """Register global exception → JSON response mappings."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return ORJSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Return structured validation errors to the client."""
        errors = [
            {
                "field": " → ".join(str(loc) for loc in err["loc"]),
                "message": err["msg"],
                "type": err["type"],
            }
            for err in exc.errors()
        ]
        logger.warning("validation_error", errors=errors, path=str(request.url))
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": 422,
                    "message": "Validation failed",
                    "details": errors,
                },
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error("unhandled_exception", error=str(exc), path=str(request.url), exc_info=True)
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "An unexpected error occurred. Please try again later.",
                },
            },
        )


def _register_routers(app: FastAPI) -> None:
    """Mount all route modules under the versioned API prefix."""

    prefix = settings.API_V1_PREFIX

    app.include_router(health.router,   prefix=prefix, tags=["Health"])
    app.include_router(auth.router,     prefix=prefix, tags=["Authentication"])
    app.include_router(users.router,    prefix=prefix, tags=["Users"])
    app.include_router(projects.router, prefix=prefix, tags=["Projects"])


# ── App instance ──────────────────────────────────────────────────────────────
app: FastAPI = create_app()


# ── Dev entrypoint ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.is_development,
        workers=1 if settings.is_development else settings.WORKERS,
        log_level="debug" if settings.DEBUG else "info",
    )
