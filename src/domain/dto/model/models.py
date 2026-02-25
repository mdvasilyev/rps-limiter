from typing import Literal

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
