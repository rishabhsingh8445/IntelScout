import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .exceptions import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from .logging_config import configure_logging
from .middleware import RequestContextMiddleware
from .routers import alerts, battlecards, briefing, competitors, matrix, search

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings.validate_for_production()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if os.getenv("DISABLE_SCHEDULER", "").lower() not in ("1", "true", "yes"):
        from .scheduler import start_scheduler

        start_scheduler()

    yield
    # Shutdown (nothing needed currently)


app = FastAPI(
    title="IntelScout API",
    description="AI-Powered Competitive Intelligence Platform Backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(RequestContextMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list or ["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-Id", "X-User-Id"],
)

app.add_exception_handler(Exception, unhandled_exception_handler)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


app.include_router(competitors.router)
app.include_router(battlecards.router)
app.include_router(matrix.router)
app.include_router(briefing.router)
app.include_router(search.router)
app.include_router(alerts.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "IntelScout API is running"}


@app.get("/api/ready")
async def readiness_check():
    from sqlalchemy import text
    from .database import AsyncSessionLocal

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ready", "database": "ok"}
    except Exception:
        from fastapi import HTTPException

        raise HTTPException(status_code=503, detail="Database unavailable")

