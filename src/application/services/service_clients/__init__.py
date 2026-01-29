"""External service clients module."""

from .booking import BookingClient, BookingClientProvider
from .model_dispatcher import ModelDispatcherClient, ModelDispatcherClientProvider
from .model_registry import ModelRegistryClient, ModelRegistryClientProvider
from .notificator import NotificatorClient, NotificatorClientProvider
from .prometheus import PrometheusClient, PrometheusClientProvider

__all__ = [
    "BookingClient",
    "BookingClientProvider",
    "ModelDispatcherClient",
    "ModelDispatcherClientProvider",
    "ModelRegistryClient",
    "ModelRegistryClientProvider",
    "NotificatorClient",
    "NotificatorClientProvider",
    "PrometheusClient",
    "PrometheusClientProvider",
]
