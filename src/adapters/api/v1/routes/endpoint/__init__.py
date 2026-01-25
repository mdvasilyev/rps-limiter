"""API v1 routes endpoint module."""

from .logs_processor import logs_processor_router

__all__ = [
    "logs_processor_router",
]
