"""
Therapity — Main Application Factory
Assembles all routers and middleware into the FastAPI app.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request

from app.config import get_settings
from app.database import create_tables

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    # Create tables on startup (dev only — use Alembic in production)
    if settings.DEBUG:
        await create_tables()
        print("📦 Database tables created/verified")
    yield
    print(f"👋 Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=f"{settings.APP_NAME} API",
    version=settings.APP_VERSION,
    description="Therapity — AI-Powered Cognitive Mindset Operating System",
    lifespan=lifespan,
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- No-Cache Middleware for dynamic endpoints ---
@app.middleware("http")
async def add_no_cache_header(request: Request, call_next):
    response = await call_next(request)
    if any(request.url.path.startswith(p) for p in ["/api/v1/chat", "/api/v1/tasks", "/api/v1/cohort"]):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


# --- Register Routers ---
from app.routers import auth, chat, diary, tasks, aoa, profile, health

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(diary.router)
app.include_router(tasks.router)
app.include_router(aoa.router)
app.include_router(profile.router)
app.include_router(health.router)


# --- Root endpoint ---
@app.get("/", include_in_schema=False)
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
