"""DTO module."""

from .base import PaginatedDTO
from .booking import Reservation, Slot, Unbook, User, WarnUnbooking
from .events import FetchAndProcessLogsEvent
from .metric import Metric, MetricValue
from .model import (
    EndpointDTO,
    InstanceDTO,
    ModelDTO,
    ModelIncreaseDTO,
    ModelRpsDTO,
    ModelState,
    PaginatedModelDTO,
    RunningModelsQuery,
    StorageDTO,
    TagDTO,
)
from .scale import Scale

__all__ = [
    "PaginatedDTO",
    "Unbook",
    "WarnUnbooking",
    "Metric",
    "MetricValue",
    "ModelRpsDTO",
    "ModelIncreaseDTO",
    "ModelState",
    "ModelDTO",
    "InstanceDTO",
    "Scale",
    "Reservation",
    "User",
    "Slot",
    "FetchAndProcessLogsEvent",
    "EndpointDTO",
    "InstanceDTO",
    "StorageDTO",
    "TagDTO",
    "PaginatedModelDTO",
    "RunningModelsQuery",
]
