import asyncio
from datetime import UTC, datetime

from dishka import Provider, Scope, provide
from faststream.rabbit import RabbitBroker
from loguru import logger

from src.core.configurations.config import GlobalConfig


class SignalPublisher:
    def __init__(self, broker: RabbitBroker, queue: str) -> None:
        self._broker = broker
        self._queue = queue

        self._stop_event = asyncio.Event()
        self._task: asyncio.Task | None = None

    async def _publish_logs_signal(self) -> None:
        """Publish signal for logs processing."""
        payload = {
            "event": "FETCH_AND_PROCESS_LOGS",
            "triggered_at": datetime.now(UTC).isoformat(),
        }

        try:
            await self._broker.publish(payload, queue=self._queue)
            logger.debug(
                "Published logs fetch signal to queue='{}'",
                self._queue,
            )
        except Exception:
            logger.exception("Failed to publish logs fetch signal")
            raise

    async def _periodic_publish_logs_signal(self, interval: int) -> None:
        logger.info(
            "Periodic logs signal publisher started (interval={}s)",
            interval,
        )

        try:
            while not self._stop_event.is_set():
                await self._publish_logs_signal()

                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=interval,
                    )
                except asyncio.TimeoutError:
                    continue
        finally:
            logger.info("Periodic logs signal publisher stopped")

    def start(self, interval: int) -> None:
        """Start periodic publishing."""
        if self._task is not None:
            raise RuntimeError("SignalPublisher already started")

        self._stop_event.clear()
        self._task = asyncio.create_task(self._periodic_publish_logs_signal(interval))

    async def stop(self) -> None:
        """Stop periodic publishing gracefully."""
        if self._task is None:
            return

        logger.info("Stopping SignalPublisher")

        self._stop_event.set()
        await self._task

        self._task = None


class SignalPublisherProvider(Provider):
    @provide(scope=Scope.APP)
    def sigal_publisher(
        self, broker: RabbitBroker, config: GlobalConfig
    ) -> SignalPublisher:
        return SignalPublisher(broker, config.rabbitmq.logs_queue)
