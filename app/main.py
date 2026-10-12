from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.config import get_settings
from app.logging_config import configure_logging
from app.routers import estimations


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.APP_ENV)
    structlog.get_logger().info("application_started", environment=settings.APP_ENV)
    yield
    structlog.get_logger().info("application_shutdown")


app = FastAPI(
    title="Estimador CAG",
    description="Sistema de estimacion de software con arquitectura CAG",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(estimations.router)


@app.get("/health")
async def health():
    return {"status": "healthy"}