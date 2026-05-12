import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings
from app.database import engine
from app.models.base import Base
from app.routers import analytics, health, pull_requests, webhook

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting PR Review Bot API")
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="PR Review Bot",
        description="Automated code review powered by GPT-4o + RAG",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(webhook.router)
    app.include_router(pull_requests.router, prefix="/api")
    app.include_router(analytics.router, prefix="/api")

    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    return app


app = create_app()
