import json
from typing import Any

from dishka import Provider, Scope, provide
from httpx import AsyncClient, Response
from loguru import logger
from starlette import status

from src.core.configurations.config import GlobalConfig
from src.domain.dto import ModelInfo

from .base import BaseServiceClient


class ModelRegistryClient(BaseServiceClient):
    async def find_running_models(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        sort: str | None = None,
        filters: dict | None = None,
    ) -> Response:
        params: dict[str, Any] = {
            "offset": offset,
            "limit": limit,
        }

        if sort:
            params["sort"] = sort

        if filters:
            params["filters"] = json.dumps(filters)

        return await self._request(
            method="GET",
            path="/v2/models/running/find-by",
            params=params,
        )

    @staticmethod
    def _to_model_info(model_data: dict[str, Any]) -> ModelInfo:
        """Конвертирует сырые данные в объект ModelInfo"""
        try:
            return ModelInfo(
                name=model_data.get("name"),
                address=model_data.get("instance", {}).get("address"),
                endpoints={
                    endpoint.get("path") for endpoint in model_data.get("endpoints", [])
                },
                replicas=model_data.get("instance", {}).get("replicas"),
                owner_id=model_data.get("instance", {}).get("ownerId"),
            )
        except Exception as e:
            logger.error("Failed to validate model data: {}. Error: {}", model_data, e)
            raise

    @staticmethod
    async def _check_and_parse_response(response: Response) -> dict[str, Any]:
        """Проверяет успешность ответа и возвращает его JSON-тело."""
        if response.status_code != status.HTTP_200_OK:
            logger.error(
                "ModelRegistry request failed with status {}: {}",
                response.status_code,
                response.text,
            )
            raise Exception("Model registry service is unavailable")
        return response.json()

    async def find_all_running_models(self) -> list[ModelInfo]:
        offset = 0
        results: list[ModelInfo] = []

        while True:
            response = await self.find_running_models(
                offset=offset,
                limit=50,
                sort="name",
            )

            result = await self._check_and_parse_response(response)

            items = result.get("items", [])

            results.extend(items)

            if not items:
                break

            offset += len(items)

        return results


class ModelRegistryClientProvider(Provider):
    @provide(scope=Scope.APP)
    def model_registry_client(
        self, config: GlobalConfig, client: AsyncClient
    ) -> ModelRegistryClient:
        return ModelRegistryClient(config.model_registry.url, client)
