from typing import Any

from httpx import Response
from loguru import logger
from starlette import status

from src.domain.dto import (
    DeleteReservationQuery,
    DeleteReservationSlotQuery,
    GetReservationQuery,
    GetReservationsQuery,
    PaginatedReservationDTO,
    ReservationDTO,
    SlotDTO,
    UserDTO,
)
from src.domain.interfaces.services import IBooking

from .base import BaseServiceClient


class BookingClient(BaseServiceClient, IBooking):
    @staticmethod
    def _to_dto(model_data: dict[str, Any]) -> ReservationDTO:
        """Конвертирует сырые данные в объект ReservationDTO"""
        try:
            return ReservationDTO(
                id=model_data.get("id"),
                user=UserDTO(
                    id=model_data.get("user").get("id"),
                    name=model_data.get("user").get("name"),
                ),
                model_name=model_data.get("model_name"),
                config_id=model_data.get("config_id"),
                model_id=model_data.get("model_id"),
                slots=[
                    SlotDTO(
                        start=slot.get("start"),
                        end=slot.get("end"),
                        id=slot.get("id"),
                    )
                    for slot in model_data.get("slots", [])
                ],
            )
        except Exception as e:
            logger.error("Failed to validate model data: {}. Error: {}", model_data, e)
            raise

    def _to_dto_paginated(self, model_data: dict[str, Any]) -> PaginatedReservationDTO:
        """Конвертирует сырые данные в объект PaginatedReservationDTO"""
        try:
            return PaginatedReservationDTO(
                items=[self._to_dto(item) for item in model_data.get("items", [])],
                total=model_data.get("total"),
                page=model_data.get("page"),
                page_size=model_data.get("page_size"),
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

    @staticmethod
    async def _check_and_parse_text_response(response: Response) -> str:
        """Проверяет успешность ответа и возвращает его TEXT-тело."""
        if response.status_code != status.HTTP_200_OK:
            logger.error(
                "Booking request failed with status {}: {}",
                response.status_code,
                response.text,
            )
            raise Exception("Booking service is unavailable")
        return response.text

    async def get_reservations(
        self,
        query: GetReservationsQuery,
    ) -> list[ReservationDTO]:
        response = await self._request(
            method="GET",
            path="/reservations",
            params=query.model_dump(exclude_none=True),
        )

        data = await self._check_and_parse_response(response)
        items = self._to_dto_paginated(data)

        return items.items

    async def get_reservation(self, query: GetReservationQuery) -> ReservationDTO:
        response = await self._request(
            method="GET",
            path=f"/reservations/{query.reservation_id}",
        )

        data = await self._check_and_parse_response(response)

        return self._to_dto(data)

    async def delete_reservation(self, query: DeleteReservationQuery) -> str:
        response = await self._request(
            method="DELETE",
            path=f"/reservations/{query.reservation_id}",
        )

        return await self._check_and_parse_text_response(response)

    async def delete_reservation_slot(self, query: DeleteReservationSlotQuery) -> str:
        response = await self._request(
            method="DELETE",
            path=f"/reservations/{query.reservation_id}/slot-usage/{query.slot_usage_id}",
        )

        return await self._check_and_parse_text_response(response)
