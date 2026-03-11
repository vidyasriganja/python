from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.routes import agent, health
from core.config import get_settings
from core.database import init_db, create_tables
from core.logging import setup_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(debug=settings.debug)
    logger = get_logger("guardian.main")

    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Init DB
    init_db(settings.database_url)
    await create_tables()
    logger.info("Database initialised")

    yield

    logger.info("Guardian shutting down")


settings = get_settings()

app = FastAPI(
    title       = settings.app_name,
    version     = settings.app_version,
    description = "AI-powered dependency management system",
    lifespan    = lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(agent.router,  prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    return {
        "app":     settings.app_name,
        "version": settings.app_version,
        "docs":    "/docs",
        "health":  "/api/v1/health",
    }
