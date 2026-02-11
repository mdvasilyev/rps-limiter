from dishka import Provider, Scope, provide
from httpx import AsyncClient

from src.core.configurations.config import GlobalConfig
from src.domain.interfaces.service_clients import IModelDispatcherClient

from .base import BaseServiceClient


class ModelDispatcherClient(BaseServiceClient, IModelDispatcherClient):
    async def uninstall(self, *, model_id: str) -> dict:
        payload = {"model_id": model_id}

        return await self._request(
            method="POST",
            path="/v1/command/uninstall",
            json=payload,
        )

    async def scale(self, model_id: str, replicas: int) -> dict:
        payload = {
            "model_id": model_id,
            "replicas": replicas,
        }

        return await self._request(
            method="POST",
            path="/v1/command/scale",
            json=payload,
        )

    async def saga_status(self, saga_id: str) -> dict:
        return await self._request(
            method="GET",
            path=f"/v1/saga/{saga_id}",
        )


class ModelDispatcherClientProvider(Provider):
    @provide(scope=Scope.APP)
    def model_dispatcher_client(
        self, config: GlobalConfig, client: AsyncClient
    ) -> ModelDispatcherClient:
        return ModelDispatcherClient(config.model_dispatcher.url, client)
