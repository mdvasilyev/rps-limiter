from typing import Any

from httpx import Response
from loguru import logger
from starlette import status

from src.domain.dto import Reservation, Slot, User
from src.domain.interfaces.service_clients import IBookingClient

from .base import BaseServiceClient


class BookingClient(BaseServiceClient, IBookingClient):
    @staticmethod
    def _to_reservation(model_data: dict[str, Any]) -> Reservation:
        """Конвертирует сырые данные в объект Response"""
        try:
            return Reservation(
                id=model_data.get("id"),
                user=User(
                    id=model_data.get("user").get("id"),
                    name=model_data.get("user").get("name"),
                ),
                model_name=model_data.get("model_name"),
                config_id=model_data.get("config_id"),
                model_id=model_data.get("model_id"),
                slots=[
                    Slot(start=slot.start, end=slot.end, id=slot.id)
                    for slot in model_data.get("slots")
                ],
            )
        except Exception as e:
            logger.error("Failed to validate model data: {}. Error: {}", model_data, e)
            raise

    @staticmethod
    async def _check_and_parse_response(response: Response) -> dict[str, Any]:
        """Проверяет успешность ответа и возвращает его JSON-тело."""
        if response.status_code != status.HTTP_200_OK:
            logger.error(
                "Booking request failed with status {}: {}",
                response.status_code,
                response.text,
            )
            raise Exception("Booking service is unavailable")
        return response.json()

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
        results: list[Reservation] = []

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

        response = await self._request(
            method="GET",
            path="/api/v1/reservations",
            params=params,
        )

        result = await self._check_and_parse_response(response)

        items = result.get("items", [])

        for reservation in items:
            results.append(self._to_reservation(reservation))

        return results

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
