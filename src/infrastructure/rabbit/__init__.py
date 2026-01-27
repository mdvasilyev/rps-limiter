"""Infrastructure RabbitMQ module."""

from .publisher import periodic_publish_logs_signal

__all__ = [
    "periodic_publish_logs_signal",
]
