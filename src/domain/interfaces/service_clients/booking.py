from abc import ABC, abstractmethod

from src.domain.dto import Reservation


class IBookingClient(ABC):
    @abstractmethod
    async def get_reservations(
        self,
        *,
        model_name: str | None = None,
        user_id: str | None = None,
        min_start_time: str | None = None,
        max_start_time: str | None = None,
        min_end_time: str | None = None,
        max_end_time: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "start_time",
        sort_order: str = "asc",
    ) -> list[Reservation]:
        pass

    @abstractmethod
    async def get_reservation(self, reservation_id: str) -> dict:
        pass

    @abstractmethod
    async def delete_reservation(self, reservation_id: str) -> str:
        pass
