"""API v1 routes module."""

from src.adapters.api.v1.routes.endpoint import logs_processor_router

api_router_list = [
    logs_processor_router,
]

__all__ = [
    "api_router_list",
]
