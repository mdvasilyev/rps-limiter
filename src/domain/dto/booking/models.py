from pydantic import BaseModel


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
