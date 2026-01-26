from faststream.rabbit import RabbitBroker

from src.core.configurations import get_config


def create_rabbit_broker() -> RabbitBroker:
    """Create a RabbitMQ broker."""
    return RabbitBroker(get_config().rabbitmq.url)
