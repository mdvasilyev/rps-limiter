from typing import Any

from httpx import Response
from loguru import logger
from starlette import status

from src.domain.dto.model import ScaleQuery, UninstallQuery
from src.domain.dto.saga import SagaDTO, SagaQuery, StepDTO
from src.domain.interfaces.services import IModelDispatcher

from .base import BaseServiceClient


class ModelDispatcherClient(BaseServiceClient, IModelDispatcher):
    @staticmethod
    def _to_dto(model_data: dict[str, Any]) -> SagaDTO:
        """Конвертирует сырые данные в объект ModelInfo"""
        try:
            return SagaDTO(
                created_at=model_data.get("createdAt"),
                current_step=model_data.get("current_step"),
                id=model_data.get("id"),
                model_id=model_data.get("modelId"),
                status=model_data.get("status"),
                steps=[
                    StepDTO(
                        created_at=step.get("createdAt"),
                        id=step.get("id"),
                        name=step.get("name"),
                        status=step.get("status"),
                        updated_at=step.get("updatedAt"),
                    )
                    for step in model_data.get("steps", [])
                ],
                type=model_data.get("type"),
                updated_at=model_data.get("updatedAt"),
            )
        except Exception as e:
            logger.error("Failed to validate model data: {}. Error: {}", model_data, e)
            raise

    @staticmethod
    async def _check_and_parse_response(response: Response) -> dict[str, Any]:
        """Проверяет успешность ответа и возвращает его JSON-тело."""
        if response.status_code != status.HTTP_200_OK:
            logger.error(
                "ModelDispatcher request failed with status {}: {}",
                response.status_code,
                response.text,
            )
            raise Exception("Model dispatcher service is unavailable")
        return response.json()

    async def uninstall(self, query: UninstallQuery) -> SagaDTO:
        response = await self._request(
            method="POST",
            path="/command/uninstall",
            json=query.model_dump(),
        )

        data = await self._check_and_parse_response(response)

        return self._to_dto(data)

    async def scale(self, query: ScaleQuery) -> SagaDTO:
        response = await self._request(
            method="POST",
            path="/command/scale",
            json=query.model_dump(),
        )

        data = await self._check_and_parse_response(response)

        return self._to_dto(data)

    async def saga_status(self, query: SagaQuery) -> SagaDTO:
        response = await self._request(
            method="GET",
            path=f"/saga/{query.saga_id}",
        )

        data = await self._check_and_parse_response(response)

        return self._to_dto(data)
