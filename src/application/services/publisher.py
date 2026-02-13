import asyncio

from faststream.rabbit import RabbitBroker, RabbitExchange
from loguru import logger

from src.domain.dto import FetchAndProcessLogsEvent
from src.domain.interfaces import ISignalPublisher


class SignalPublisher(ISignalPublisher):
    def __init__(
        self, broker: RabbitBroker, exchange: RabbitExchange, queue: str
    ) -> None:
        self._broker = broker
        self._exchange = exchange
        self._queue = queue

        self._stop_event = asyncio.Event()
        self._task: asyncio.Task | None = None

    async def _publish_logs_signal(self) -> None:
        """Publish signal for logs processing."""
        event = FetchAndProcessLogsEvent()

        try:
            await self._broker.publish(
                event.model_dump(mode="json"),
                queue=self._queue,
                exchange=self._exchange,
            )
            logger.debug(
                "Published logs fetch signal to queue='{}'",
                self._queue,
            )
        except Exception:
            logger.exception("Failed to publish logs fetch signal")
            raise

    async def _periodic_publish_logs_signal(self, interval: int) -> None:
        """Periodically publish signal for logs processing."""
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
