from abc import ABC, abstractmethod

from src.domain.dto.booking import (
    DeleteReservationQuery,
    DeleteReservationSlotQuery,
    GetReservationQuery,
    GetReservationsQuery,
    ReservationDTO,
)


class IBooking(ABC):
    @abstractmethod
    async def get_reservations(
        self, query: GetReservationsQuery
    ) -> list[ReservationDTO]:
        pass

    @abstractmethod
    async def get_reservation(self, query: GetReservationQuery) -> ReservationDTO:
        pass

    @abstractmethod
    async def delete_reservation(self, query: DeleteReservationQuery) -> str:
        pass

    @abstractmethod
    async def delete_reservation_slot(self, query: DeleteReservationSlotQuery) -> str:
        pass
