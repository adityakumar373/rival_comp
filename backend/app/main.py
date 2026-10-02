from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logger import get_logger
from app.services.scheduler_service import start_scheduler, stop_scheduler

# Routers
from app.api.competitor import router as competitor_router
from app.api.source import router as source_router
from app.api.scraper import router as scraper_router
from app.api.changes import router as changes_router
from app.api.insights import router as insights_router
from app.api.alerts import router as alerts_router
from app.api.dashboard import router as dashboard_router
from app.api.discovery import router as discovery_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "app_startup",
        extra={"environment": settings.ENVIRONMENT, "scheduler_enabled": settings.SCHEDULER_ENABLED},
    )
    # Start embedded background scheduler
    start_scheduler()
    yield
    # Stop scheduler on shutdown
    stop_scheduler()
    logger.info("app_shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS — allow the frontend (and dev tools like Swagger) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(competitor_router)
app.include_router(source_router)
app.include_router(scraper_router)
app.include_router(changes_router)
app.include_router(insights_router)
app.include_router(alerts_router)
app.include_router(dashboard_router)
app.include_router(discovery_router)

@app.get("/health")
def health():
    """Health-check endpoint."""
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "scheduler_enabled": settings.SCHEDULER_ENABLED,
    }

# Serve frontend static files from root project frontend directory
_frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if not _frontend_dir.is_dir():
    _frontend_dir = Path(__file__).resolve().parent.parent / "frontend"

if _frontend_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(_frontend_dir), html=True), name="frontend")