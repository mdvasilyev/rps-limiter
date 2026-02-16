import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel

from src.domain.dto import PaginatedDTO


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


class EndpointDTO(BaseModel):
    description: str
    id: int
    path: str


class InstanceDTO(BaseModel):
    address: str | None
    id: int
    owner_id: str | None
    replicas: int


class StorageDTO(BaseModel):
    artifact_id: int | None
    id: int
    revision: str
    type: Literal["s3", "nfs"]
    uri: str


class TagDTO(BaseModel):
    id: int
    tag: str


class ModelDTO(BaseModel):
    configuration: dict[str, str]
    deleted: bool
    endpoints: list[EndpointDTO]
    hf_repo_id: str | None
    id: str
    instance: InstanceDTO
    name: str
    status: Literal[
        "CREATED",
        "DOWNLOADING",
        "DOWNLOADED",
        "STARTING",
        "RUNNING",
        "STOPPING",
        "DELETED",
    ]
    storage: StorageDTO | None
    tags: list[TagDTO]
    type: Literal["llm", "vlm"]


PaginatedModelDTO = PaginatedDTO[ModelDTO]


class RunningModelsQuery(BaseModel):
    offset: int = 0
    limit: int = 50
    sort: str | None = None
    filters: dict[str, Any] | None = None

    def to_params(self) -> dict[str, Any]:
        data = self.model_dump(exclude_none=True)

        if "filters" in data:
            data["filters"] = json.dumps(data["filters"])

        return data
