"""RabbitMQ configurations module."""

from .connection import create_rabbit_broker

__all__ = [
    "create_rabbit_broker",
]
