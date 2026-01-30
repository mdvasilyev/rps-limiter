from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, kw_only=True)
class ModelRpsDTO:
    model_name: str
    rps: float


@dataclass(slots=True)
class ModelIncreaseDTO:
    model_name: str
    requests: float


@dataclass
class ModelState:
    last_rps: float | None
    zero_since: datetime | None
