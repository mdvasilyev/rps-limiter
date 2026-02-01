from dataclasses import Field, dataclass
from datetime import datetime

from pydantic import BaseModel, ConfigDict


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


class InstanceInfo(BaseModel):
    id: int
    replicas: int
    ownerId: str | None
    address: str


class ModelInfo(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str
    instance: InstanceInfo
    name: str
    address: str
    endpoints: set[str]
    replicas: int = 0
    owner_id: str | None
