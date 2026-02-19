"""Service clients interfaces module."""

from .booking import IBooking
from .decision_maker import IDecisionMaker
from .logs_processor import ILogsProcessor
from .model_dispatcher import IModelDispatcher
from .model_load_monitor import IModelLoadMonitor
from .model_registry import IModelRegistry
from .prometheus import IPrometheus
from .publisher import IPublisher

__all__ = [
    "IBooking",
    "IDecisionMaker",
    "ILogsProcessor",
    "IModelDispatcher",
    "IModelLoadMonitor",
    "IModelRegistry",
    "IPrometheus",
    "IPublisher",
]
