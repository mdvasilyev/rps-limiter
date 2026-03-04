from pydantic import BaseModel

from .models import SlotPeriodDTO


class NotifyQuery(BaseModel):
    user_id: str
    model_name: str
    periods: list[SlotPeriodDTO]
