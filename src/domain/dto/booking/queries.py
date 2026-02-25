from typing import Literal

from pydantic import BaseModel


class GetReservationsQuery(BaseModel):
    model_name: str | None = None
    min_start_time: str | None = None
    max_start_time: str | None = None
    min_end_time: str | None = None
    max_end_time: str | None = None
    user_id: str | None = None
    page: int = 1
    page_size: int = 20
    sort_by: str = "start_time"
    sort_order: Literal["asc", "desc"] = "asc"


class GetReservationQuery(BaseModel):
    reservation_id: str


class DeleteReservationQuery(BaseModel):
    reservation_id: str


class DeleteReservationSlotQuery(BaseModel):
    reservation_id: str
    slot_usage_id: str
