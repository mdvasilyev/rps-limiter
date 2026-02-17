from typing import Literal

from pydantic import BaseModel


class Unbook(BaseModel):
    model_name: str
    user_id: str


class UserDTO(BaseModel):
    id: str
    name: str


class SlotDTO(BaseModel):
    start: int
    end: int
    id: str


class ReservationDTO(BaseModel):
    id: str
    user: UserDTO
    model_name: str
    config_id: int | None = None
    model_id: str | None = None
    slots: list[SlotDTO]


class PaginatedReservationDTO(BaseModel):
    items: list[ReservationDTO]
    total: int
    page: int
    page_size: int


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
