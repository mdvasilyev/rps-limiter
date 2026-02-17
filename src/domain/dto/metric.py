from typing import NamedTuple

from pydantic import BaseModel


class MetricValueDTO(NamedTuple):
    timestamp: float
    value: str


class MetricDTO(BaseModel):
    metric: dict[str, str]
    value: MetricValueDTO
