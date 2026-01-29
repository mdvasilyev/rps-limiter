from dishka import Provider, Scope, provide
from httpx import AsyncClient

from src.core.configurations.config import GlobalConfig

from .base import BaseServiceClient


class ModelDispatcherClient(BaseServiceClient):
    async def uninstall(self, model_id: str) -> None:
        await self._request(
            method="POST",
            path="/v1/command/uninstall",
            json={"model_id": model_id},
        )

    async def scale(self, model_id: str, replicas: int) -> None:
        await self._request(
            method="POST",
            path="/v1/command/scale",
            json={
                "model_id": model_id,
                "replicas": replicas,
            },
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
