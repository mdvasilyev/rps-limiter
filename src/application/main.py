import asyncio

from loguru import logger

from src.application.services.publisher import SignalPublisher
from src.core.configurations.config import GlobalConfig
from src.core.configurations.dishka import create_container
from src.core.configurations.faststream import create_faststream


async def main():
    container = create_container()
    app = await create_faststream(container)
    publisher = await container.get(SignalPublisher)

    @app.after_startup
    async def startup():
        logger.info("Starting up")
        config = await container.get(GlobalConfig)
        publisher.start(config.worker.interval)

    @app.after_shutdown
    async def shutdown():
        logger.info("Shutting down")
        await publisher.stop()
        await container.close()

    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
