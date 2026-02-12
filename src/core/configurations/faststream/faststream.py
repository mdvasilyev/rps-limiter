from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitExchange

from .router import create_router


def create_faststream(broker: RabbitBroker, exchange: RabbitExchange) -> FastStream:
    router = create_router(exchange)
    broker.include_router(router)

    return FastStream(broker)
