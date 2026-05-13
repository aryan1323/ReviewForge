import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings
from app.database import engine
from app.models.base import Base
from app.routers import analytics, auth, health, pull_requests, webhook
from app.routers import config_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()


def _start_worker():
    from rq import SimpleWorker
    from app.tasks.queue import redis_conn
    worker = SimpleWorker(["reviews"], connection=redis_conn)
    logger.info("rq worker starting inside API process")
    worker.work()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting PR Review Bot API")
    t = threading.Thread(target=_start_worker, daemon=True)
    t.start()
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
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(webhook.router)
    app.include_router(pull_requests.router, prefix="/api")
    app.include_router(analytics.router, prefix="/api")
    app.include_router(config_router.router, prefix="/api")

    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    return app


app = create_app()
