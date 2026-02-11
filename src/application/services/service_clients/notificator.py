from dishka import Provider, Scope, provide
from httpx import AsyncClient

from src.core.configurations.config import GlobalConfig
from src.domain.interfaces.service_clients import INotificatorClient

from .base import BaseServiceClient


class NotificatorClient(BaseServiceClient, INotificatorClient):
    async def notify(self, model_id: str, user_id: str, payload: dict) -> None:
        payload["model_id"] = model_id
        payload["user_id"] = user_id
        await self._request(
            method="POST",
            path="/notify",
            json=payload,
        )


class NotificatorClientProvider(Provider):
    @provide(scope=Scope.APP)
    def notificator_client(
        self, config: GlobalConfig, client: AsyncClient
    ) -> NotificatorClient:
        return NotificatorClient(config.notificator.url, client)
