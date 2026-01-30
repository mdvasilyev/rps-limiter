from typing import Any

from dishka import Provider, Scope, provide
from httpx import AsyncClient

from src.core.configurations.config import GlobalConfig

from .base import BaseServiceClient


class BookingClient(BaseServiceClient):
    async def get_reservations(
        self,
        *,
        model_name: str | None = None,
        user_id: str | None = None,
        min_start_time: int | None = None,
        max_start_time: int | None = None,
        min_end_time: int | None = None,
        max_end_time: int | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "start_time",
        sort_order: str = "asc",
    ) -> dict:
        params: dict[str, Any] = {
            "page": page,
            "page_size": page_size,
            "sort_by": sort_by,
            "sort_order": sort_order,
        }

        if model_name is not None:
            params["model_name"] = model_name
        if user_id is not None:
            params["user_id"] = user_id
        if min_start_time is not None:
            params["min_start_time"] = min_start_time
        if max_start_time is not None:
            params["max_start_time"] = max_start_time
        if min_end_time is not None:
            params["min_end_time"] = min_end_time
        if max_end_time is not None:
            params["max_end_time"] = max_end_time

        return await self._request(
            method="GET",
            path="/api/v1/reservations",
            params=params,
        )

    async def get_reservation(self, reservation_id: str) -> dict:
        return await self._request(
            method="GET",
            path=f"/api/v1/reservations/{reservation_id}",
        )

    async def delete_reservation(self, reservation_id: str) -> str:
        return await self._request(
            method="DELETE",
            path=f"/api/v1/reservations/{reservation_id}",
        )


class BookingClientProvider(Provider):
    @provide(scope=Scope.APP)
    def booking_client(
        self, config: GlobalConfig, client: AsyncClient
    ) -> BookingClient:
        return BookingClient(config.booking.url, client)
