import asyncio
from pathlib import Path

from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitRouter
from loguru import logger

from src.application.services import LogsProcessor
from src.core.configurations.config import get_config
from src.core.configurations.rabbit import create_rabbit_broker

config = get_config()

broker: RabbitBroker = create_rabbit_broker()
app = FastStream(broker)
router = RabbitRouter()

broker.include_router(router)


@router.subscriber(config.rabbitmq.logs_queue)
async def handle_logs_signal(message: dict):
    logger.info(
        "Received logs processing signal: {}",
        message.get("triggered_at"),
    )

    service = LogsProcessor(Path("yaml-examples/entrypoint_metrics.txt"))
    logger.info("Requests count: {}", service.count_requests())


async def main():
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
