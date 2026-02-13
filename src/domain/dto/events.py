from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class FetchAndProcessLogsEvent(BaseModel):
    type: Literal["FETCH_AND_PROCESS_LOGS"] = Field("FETCH_AND_PROCESS_LOGS")
    triggered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        data = super().model_dump(*args, **kwargs)
        return {"event": data}
