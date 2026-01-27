from .base import BaseServiceClient


class NotificatorClient(BaseServiceClient):
    async def notify(self, payload: dict) -> None:
        await self._request(
            method="POST",
            path="/notify",
            json=payload,
        )
