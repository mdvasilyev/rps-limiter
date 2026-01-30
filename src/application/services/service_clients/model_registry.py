import json
from typing import Any

from dishka import Provider, Scope, provide
from httpx import AsyncClient

from src.core.configurations.config import GlobalConfig

from .base import BaseServiceClient


class ModelRegistryClient(BaseServiceClient):
    async def find_running_models(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        sort: list[str] | None = None,
        filters: dict | None = None,
    ) -> dict:
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

    async def find_all_running_models(
        self,
        *,
        batch_size: int = 100,
        sort: list[str] | None = None,
        filters: dict | None = None,
    ) -> list[dict]:
        offset = 0
        result: list[dict] = []

        while True:
            response = await self.find_running_models(
                offset=offset,
                limit=batch_size,
                sort=sort,
                filters=filters,
            )

            items: list[dict] = response.get("items", [])
            result.extend(items)

            if len(items) < batch_size:
                break

            offset += batch_size

        return result


class ModelRegistryClientProvider(Provider):
    @provide(scope=Scope.APP)
    def model_registry_client(
        self, config: GlobalConfig, client: AsyncClient
    ) -> ModelRegistryClient:
        return ModelRegistryClient(config.model_registry.url, client)
