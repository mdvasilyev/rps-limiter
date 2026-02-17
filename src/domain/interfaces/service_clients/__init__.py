"""Service clients interfaces module."""

from .booking import IBookingClient
from .model_dispatcher import IModelDispatcherClient
from .model_registry import IModelRegistryClient
from .prometheus import IPrometheusClient

__all__ = [
    "IBookingClient",
    "IModelDispatcherClient",
    "IModelRegistryClient",
    "IPrometheusClient",
]
