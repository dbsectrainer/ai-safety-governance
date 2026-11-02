"""FastAPI application entry point."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import text

from .api.routers import (
    auth,
    compliance,
    dashboard,
    models,
    monitoring,
    security,
    settings,
    users,
)
from .database import engine, init_db
from .database.bootstrap import ensure_default_roles

logger = logging.getLogger(__name__)

DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"


def _cors_origins() -> list[str]:
    return [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS).split(",")
        if origin.strip()
    ]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialise the schema and optional bootstrap administrator."""
    init_db()
    ensure_default_roles()
    try:
        from .scripts.seed_admin import ensure_admin_from_env

        ensure_admin_from_env()
    except Exception:
        logger.exception("Administrator bootstrap failed")
    yield


app = FastAPI(
    title="AI Safety Governance Platform",
    description=(
        "API for AI model monitoring, compliance records, user administration "
        "and platform security posture."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS. Origins are explicit so credentialed requests are safe.
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["Content-Type", "Authorization"],
    max_age=3600,
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add baseline browser security headers to every response."""
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("X-XSS-Protection", "1; mode=block")
    response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
    return response


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(compliance.router, prefix="/api/v1/compliance", tags=["compliance"])
app.include_router(models.router, prefix="/api/v1/models", tags=["models"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(security.router, prefix="/api/v1/security", tags=["security"])
app.include_router(settings.router, prefix="/api/v1/settings", tags=["settings"])


@app.get("/", include_in_schema=False)
async def root():
    """Small service descriptor for humans and uptime checks."""
    return {
        "name": "AI Safety Governance Platform",
        "version": app.version,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Liveness probe. Does not require a database connection."""
    return {
        "status": "healthy",
        "service": "ai-safety-governance",
        "version": app.version,
    }


@app.get("/ready", tags=["health"])
async def readiness_check():
    """Readiness probe that verifies database connectivity."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception:
        logger.exception("Readiness check failed")
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "database": "unavailable"},
        )


@app.get("/metrics", include_in_schema=False)
async def metrics():
    """Minimal Prometheus-compatible liveness metric.

    The platform does not yet export request or model metrics; this endpoint
    intentionally reports only that the process is up.
    """
    return PlainTextResponse(
        "# HELP ai_safety_governance_up Process liveness\n"
        "# TYPE ai_safety_governance_up gauge\n"
        "ai_safety_governance_up 1\n",
        media_type="text/plain; version=0.0.4",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
    )
