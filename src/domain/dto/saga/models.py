from typing import Literal

from pydantic import BaseModel


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
