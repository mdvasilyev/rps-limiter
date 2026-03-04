from pydantic import BaseModel


class SlotPeriodDTO(BaseModel):
    start: float
    end: float
