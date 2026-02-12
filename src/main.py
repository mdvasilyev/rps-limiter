import asyncio

from dishka.integrations.faststream import setup_dishka
from faststream.rabbit import RabbitBroker, RabbitExchange
from loguru import logger

from src.application.services.publisher import SignalPublisher
from src.core.configurations.config import GlobalConfig
from src.core.configurations.faststream import create_faststream
from src.ioc import create_container


async def main():
    container = create_container()
    broker = await container.get(RabbitBroker)
    exchange = await container.get(RabbitExchange)
    app = create_faststream(broker, exchange)
    publisher = await container.get(SignalPublisher)
    setup_dishka(container, app)

    @app.after_startup
    async def startup():
        logger.info("Starting up")
        config = await container.get(GlobalConfig)
        publisher.start(config.worker.process_interval)

    @app.after_shutdown
    async def shutdown():
        logger.info("Shutting down")
        await publisher.stop()
        await container.close()

    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
