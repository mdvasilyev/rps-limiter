from typing import NamedTuple

from pydantic import BaseModel


class MetricValue(NamedTuple):
    timestamp: float
    value: str


class Metric(BaseModel):
    metric: dict[str, str]
    value: MetricValue
