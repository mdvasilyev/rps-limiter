"""Service clients interfaces module."""

from .booking import IBookingClient
from .model_dispatcher import IModelDispatcherClient
from .model_registry import IModelRegistryClient
from .notificator import INotificatorClient
from .prometheus import IPrometheusClient

__all__ = [
    "IBookingClient",
    "IModelDispatcherClient",
    "IModelRegistryClient",
    "INotificatorClient",
    "IPrometheusClient",
]
