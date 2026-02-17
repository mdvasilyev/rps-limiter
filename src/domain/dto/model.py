import json
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


class ModelRpsDTO(BaseModel):
    model_name: str
    rps: float


class ModelIncreaseDTO(BaseModel):
    model_name: str
    requests: float


class ModelRpsIncreaseDTO(BaseModel):
    model_name: str
    rps: float
    requests: float


class ModelState(BaseModel):
    last_rps: float | None = None
    zero_since: datetime | None = None


class EndpointDTO(BaseModel):
    description: str
    id: int
    path: str


class InstanceDTO(BaseModel):
    address: str | None = None
    id: int
    owner_id: str | None = None
    replicas: int


class StorageDTO(BaseModel):
    artifact_id: int | None = None
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
    hf_repo_id: str | None = None
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
    storage: StorageDTO | None = None
    tags: list[TagDTO]
    type: Literal["llm", "vlm"]


class PaginatedModelDTO(BaseModel):
    limit: int
    offset: int
    total: int
    items: list[ModelDTO]


class RunningModelsQuery(BaseModel):
    offset: int = 0
    limit: int = 50
    sort: str | None = None
    filters: dict[str, Any] | None = None

    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        data = super().model_dump(*args, **kwargs, exclude_none=True)

        if "filters" in data:
            data["filters"] = json.dumps(data["filters"])

        return data
