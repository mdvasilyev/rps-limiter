from datetime import UTC, datetime

from pydantic import BaseModel, Field


class GetIdleModelQuery(BaseModel):
    user_id: str
    model_name: str


class PostIdleModelQuery(BaseModel):
    user_id: str
    model_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DeleteIdleModelQuery(BaseModel):
    user_id: str
    model_name: str
