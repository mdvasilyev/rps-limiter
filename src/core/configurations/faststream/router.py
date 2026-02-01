from dishka import AsyncContainer
from faststream.rabbit import RabbitRouter

from src.application.workers import handle_logs_signal
from src.core.configurations.config import GlobalConfig


async def create_router(container: AsyncContainer) -> RabbitRouter:
    router = RabbitRouter()

    config = await container.get(GlobalConfig)

    @router.subscriber(config.rabbitmq.logs_queue)
    async def handle_logs(message: dict) -> None:
        await handle_logs_signal(message, container)

    return router
