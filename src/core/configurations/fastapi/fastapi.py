from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI

from src.adapters.api.v1.routes import api_router_list
from src.core.configurations import get_config


@asynccontextmanager
async def lifespan(_: FastAPI):
    config = get_config()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(stub, IntervalTrigger(seconds=config.worker.interval))
    scheduler.start()

    yield

    scheduler.shutdown()


def setup_routers(app: FastAPI) -> None:
    for router in api_router_list:
        app.include_router(router)


def get_app() -> FastAPI:
    app = FastAPI(
        title="RPS Limiter",
        description="Service for managing model lifecycle based on RPS",
        version="0.1.0",
        lifespan=lifespan,
    )

    setup_routers(app)

    return app


async def stub():
    # Ваша логика: fetch из сервиса, transform, save в DB
    pass
