import asyncio
from contextlib import asynccontextmanager, suppress

import aiohttp
from fastapi import FastAPI
from loguru import logger

from src.adapters.api.v1.routes import api_router_list
from src.application.services.service_clients import ServiceClients
from src.core.configurations.config import GlobalConfig
from src.core.configurations.dishka import container
from src.core.configurations.rabbit import create_rabbit_broker
from src.infrastructure.rabbit import periodic_publish_logs_signal


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI application")

    config: GlobalConfig = container.get(GlobalConfig)

    session = aiohttp.ClientSession()
    app.state.service_clients = ServiceClients(config, session=session)

    broker = create_rabbit_broker()

    await broker.connect()
    app.state.broker = broker

    logger.info("RabbitMQ broker connected")

    stop_event = asyncio.Event()

    task = asyncio.create_task(
        periodic_publish_logs_signal(
            stop_event=stop_event,
            broker=broker,
        )
    )

    app.state.periodic_task = task
    app.state.periodic_stop_event = stop_event

    logger.info("Periodic logs signal publisher task started")

    yield

    container.close()

    logger.info("Shutting down FastAPI application")

    stop_event.set()
    task.cancel()

    with suppress(asyncio.CancelledError):
        await task

    await app.state.service_clients.close()

    await broker.stop()
    logger.info("RabbitMQ broker stopped")


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
