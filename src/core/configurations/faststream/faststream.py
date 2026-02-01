from dishka import AsyncContainer
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from .router import create_router


async def create_faststream(container: AsyncContainer) -> FastStream:
    broker = await container.get(RabbitBroker)
    broker.include_router(await create_router(container))
    return FastStream(broker)
