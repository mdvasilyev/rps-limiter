from faststream.rabbit import RabbitBroker

from src.core.configurations.config import GlobalConfig
from src.core.configurations.dishka import container


def create_rabbit_broker() -> RabbitBroker:
    """Create a RabbitMQ broker."""
    config: GlobalConfig = container.get(GlobalConfig)

    return RabbitBroker(config.rabbitmq.url)
