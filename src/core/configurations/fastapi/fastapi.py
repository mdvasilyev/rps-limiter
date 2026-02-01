import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from faststream.rabbit import RabbitBroker
from loguru import logger

from src.application.services.publisher import SignalPublisher
from src.core.configurations.config import GlobalConfig
from src.core.configurations.dishka import container


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI application")

    broker: RabbitBroker = container.get(RabbitBroker)

    await broker.connect()
    app.state.broker = broker

    logger.info("RabbitMQ broker connected")

    stop_event = asyncio.Event()

    periodic_publisher: SignalPublisher = container.get(SignalPublisher)

    task = asyncio.create_task(
        periodic_publisher.periodic_publish_logs_signal(
            stop_event=stop_event,
            interval=container.get(GlobalConfig).worker.interval,
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

    await broker.stop()
    logger.info("RabbitMQ broker stopped")


def get_app() -> FastAPI:
    app = FastAPI(
        title="RPS Limiter",
        description="Service for managing model lifecycle based on RPS",
        version="0.1.0",
        lifespan=lifespan,
    )

    return app
