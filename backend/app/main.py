import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.core.redis import get_redis, close_redis
from app.api.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ticketing.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    logger.info("Initializing %s in %s mode...", settings.PROJECT_NAME, settings.ENVIRONMENT)
    try:
        # Initialize Redis connection pool
        await get_redis()
    except Exception as e:
        logger.warning("Could not initialize Redis on startup: %s", e)

    try:
        # Auto-create tables if running in development / test
        await init_db()
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.warning("Database init_db warning (may require PostgreSQL to be running): %s", e)

    yield

    # Shutdown sequence
    logger.info("Shutting down %s...", settings.PROJECT_NAME)
    await close_redis()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend & AI Architecture for AI-Powered Online Ticketing & Booking Assistant",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/web", response_class=HTMLResponse, tags=["Web"])
async def web_ui():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return "<h1>Web UI not found</h1>"


@app.get("/", tags=["System"])
async def root(request: Request):
    accept = request.headers.get("accept", "")
    index_file = os.path.join(STATIC_DIR, "index.html")
    if "text/html" in accept and os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "project": settings.PROJECT_NAME,
        "version": "1.0.0",
        "documentation": "/docs",
        "web_ui": "/web",
        "workflow_supported": [
            "1. Discovery",
            "2. Recommendation",
            "3. Availability",
            "4. Selection",
            "5. Booking",
            "6. Confirmation",
            "7. Post-booking"
        ],
        "anti_overbooking_engine": "Redis Distributed Lock + PostgreSQL Row-level Lock (FOR UPDATE)"
    }


@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER
    }

