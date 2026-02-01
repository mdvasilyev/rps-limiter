import asyncio
from datetime import UTC, datetime

from dishka import Provider, Scope, provide
from faststream.rabbit import RabbitBroker
from loguru import logger

from src.core.configurations.config import GlobalConfig


class SignalPublisher:
    def __init__(self, broker: RabbitBroker, queue: str):
        self._broker = broker
        self._queue = queue

    async def _publish_logs_signal(self) -> None:
        """Publish signal for logs processing."""
        payload = {
            "event": "FETCH_AND_PROCESS_LOGS",
            "triggered_at": datetime.now(UTC).isoformat(),
        }

        try:
            await self._broker.publish(payload, queue=self._queue)
            logger.debug("Published logs fetch signal to queue='{}'", self._queue)
        except Exception:
            logger.exception("Failed to publish logs fetch signal")
            raise

    async def periodic_publish_logs_signal(
        self,
        stop_event: asyncio.Event,
        interval: int,
    ):
        """Periodically publish signals."""
        logger.info(
            "Periodic logs signal publisher started (interval={}s)",
            interval,
        )

        while not stop_event.is_set():
            await self._publish_logs_signal()

            try:
                await asyncio.wait_for(stop_event.wait(), timeout=interval)
            except asyncio.TimeoutError:
                continue

        logger.info("Periodic logs signal publisher stopped")


class SignalPublisherProvider(Provider):
    @provide(scope=Scope.APP)
    def sigal_publisher(
        self, broker: RabbitBroker, config: GlobalConfig
    ) -> SignalPublisher:
        return SignalPublisher(broker, config.rabbitmq.logs_queue)
