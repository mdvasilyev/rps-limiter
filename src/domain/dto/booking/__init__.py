"""Domain booking DTO module."""

from .actions import UnbookAction
from .models import PaginatedReservationDTO, ReservationDTO, SlotDTO, UserDTO
from .queries import (
    DeleteReservationQuery,
    DeleteReservationSlotQuery,
    GetReservationQuery,
    GetReservationsQuery,
)

__all__ = [
    "UnbookAction",
    "ReservationDTO",
    "PaginatedReservationDTO",
    "UserDTO",
    "SlotDTO",
    "GetReservationsQuery",
    "GetReservationQuery",
    "DeleteReservationQuery",
    "DeleteReservationSlotQuery",
]
