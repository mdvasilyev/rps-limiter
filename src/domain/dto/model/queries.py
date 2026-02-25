import json
from typing import Any

from pydantic import BaseModel, Field


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


class ScaleQuery(BaseModel):
    model_id: str = Field(alias="modelId")
    replicas: int

    model_config = {"populate_by_name": True}

    def model_dump(self, *args: Any, **kwargs: Any) -> dict:
        return super().model_dump(*args, **kwargs, by_alias=True)


class UninstallQuery(BaseModel):
    model_id: str = Field(alias="modelId")

    model_config = {"populate_by_name": True}

    def model_dump(self, *args: Any, **kwargs: Any) -> dict:
        return super().model_dump(*args, **kwargs, by_alias=True)
