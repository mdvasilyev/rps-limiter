import asyncio

import uvicorn
from dishka_faststream import setup_dishka
from faststream.rabbit import RabbitBroker, RabbitExchange
from loguru import logger

from src.core.configurations.config import GlobalConfig
from src.core.configurations.faststream import create_faststream
from src.core.database.manager import PostgresConnectionManager
from src.core.logging import setup_logging
from src.domain.interfaces.services import IPublisher
from src.healthcheck import liveness, readiness
from src.ioc import create_container


async def main():
    container = create_container()

    config = await container.get(GlobalConfig)

    setup_logging(config.logging)

    broker = await container.get(RabbitBroker)
    exchange = await container.get(RabbitExchange)
    connection_manager = await container.get(PostgresConnectionManager)
    app = create_faststream(broker, exchange)
    publisher = await container.get(IPublisher)

    setup_dishka(container, app)

    @app.after_startup
    async def startup():
        logger.info("Starting up")
        publisher.start(config.worker.process_interval)

    @app.after_shutdown
    async def shutdown():
        logger.info("Shutting down")
        await publisher.stop()
        await container.close()

    asgi_app = app.as_asgi(
        asgi_routes=[
            ("/internal/alive", liveness),
            ("/internal/ready", readiness(broker, connection_manager)),
        ]
    )

    server = uvicorn.Server(
        uvicorn.Config(asgi_app, host=config.app.host, port=config.app.port)
    )
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
