"""Exceptions module."""

from .prometheus import PrometheusError
from .worker import WorkerError

__all__ = [
    "PrometheusError",
    "WorkerError",
]
