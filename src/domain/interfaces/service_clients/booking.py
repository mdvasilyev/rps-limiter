from abc import ABC, abstractmethod

from src.domain.dto import (
    DeleteReservationQuery,
    GetReservationQuery,
    GetReservationsQuery,
    ReservationDTO,
)


class IBookingClient(ABC):
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
