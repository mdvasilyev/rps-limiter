from typing import Literal

from pydantic import BaseModel, Field


class StepDTO(BaseModel):
    created_at: str
    id: int
    name: str
    status: Literal[
        "pending",
        "in_progress",
        "completed",
        "failed",
        "compensating",
        "compensated",
        "compensation_failed",
        "failed_pending_cleanup",
        "awaiting_cleanup",
    ]
    updated_at: str


class SagaDTO(BaseModel):
    created_at: str
    current_step: int
    id: str
    model_id: str
    status: Literal[
        "created", "in_progress", "completed", "failed", "compensating", "compensated"
    ]
    steps: list[StepDTO]
    type: Literal["install", "uninstall", "upscale", "downscale", "load"]
    updated_at: str


class ScaleQuery(BaseModel):
    model_id: str = Field(alias="modelId")
    replicas: int

    model_config = {"populate_by_name": True}

    def to_payload(self) -> dict:
        return self.model_dump(by_alias=True)


class UninstallQuery(BaseModel):
    model_id: str = Field(alias="modelId")

    model_config = {"populate_by_name": True}

    def to_payload(self) -> dict:
        return self.model_dump(by_alias=True)


class SagaQuery(BaseModel):
    saga_id: str
