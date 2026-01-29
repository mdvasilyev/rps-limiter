import asyncio
from datetime import UTC, datetime

from faststream.rabbit import RabbitBroker
from loguru import logger

from src.core.configurations.config import GlobalConfig
from src.core.configurations.dishka import container


async def publish_logs_signal(
    broker: RabbitBroker,
    queue: str,
) -> None:
    """Publish signal to fetch and process logs."""
    payload = {
        "event": "FETCH_AND_PROCESS_LOGS",
        "triggered_at": datetime.now(UTC).isoformat(),
    }

    try:
        await broker.publish(payload, queue=queue)
        logger.debug("Published logs fetch signal to queue='{}'", queue)
    except Exception:
        logger.exception("Failed to publish logs fetch signal")
        raise


async def periodic_publish_logs_signal(
    stop_event: asyncio.Event,
    broker,
):
    config: GlobalConfig = container.get(GlobalConfig)

    interval = config.worker.interval
    queue = config.rabbitmq.logs_queue

    logger.info(
        "Periodic logs signal publisher started (interval={}s)",
        interval,
    )

    while not stop_event.is_set():
        await publish_logs_signal(
            broker=broker,
            queue=queue,
        )

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            continue

    logger.info("Periodic logs signal publisher stopped")
