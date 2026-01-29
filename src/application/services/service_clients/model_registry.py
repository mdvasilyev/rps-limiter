from dishka import Provider, Scope, provide
from httpx import AsyncClient

from src.core.configurations.config import GlobalConfig

from .base import BaseServiceClient


class ModelRegistryClient(BaseServiceClient):
    async def find_running_models(self, payload: dict) -> dict:
        return await self._request(
            method="POST",
            path="/v2/models/running/find-by",
            json=payload,
        )


class ModelRegistryClientProvider(Provider):
    @provide(scope=Scope.APP)
    def model_registry_client(
        self, config: GlobalConfig, client: AsyncClient
    ) -> ModelRegistryClient:
        return ModelRegistryClient(config.model_registry.url, client)
