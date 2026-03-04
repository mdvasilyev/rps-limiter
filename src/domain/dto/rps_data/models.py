from datetime import datetime

from pydantic import BaseModel


class IdleModelDTO(BaseModel):
    id: int
    user_id: str
    model_name: str
    timestamp: datetime
