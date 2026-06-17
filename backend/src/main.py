import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import competitors, battlecards, matrix, briefing, search, alerts

app = FastAPI(
    title="IntelScout API",
    description="AI-Powered Competitive Intelligence Platform Backend",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Automatically create tables for easy setup during development
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    from .scheduler import start_scheduler
    start_scheduler()

# Include routers
app.include_router(competitors.router)
app.include_router(battlecards.router)
app.include_router(matrix.router)
app.include_router(briefing.router)
app.include_router(search.router)
app.include_router(alerts.router)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "IntelScout API is running"}
