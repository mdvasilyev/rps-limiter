from .base import BaseServiceClient


class BookingClient(BaseServiceClient):
    async def create_reservation(self, payload: dict) -> dict:
        return await self._request(
            method="POST",
            path="/api/v1/reservations",
            json=payload,
        )

    async def get_reservation(self, reservation_id: str) -> dict:
        return await self._request(
            method="GET",
            path=f"/api/v1/reservations/{reservation_id}",
        )

    async def get_slot_usage(
        self,
        reservation_id: str,
        slot_id: str,
    ) -> dict:
        return await self._request(
            method="GET",
            path=f"/api/v1/reservations/{reservation_id}/slot-usage/{slot_id}",
        )
