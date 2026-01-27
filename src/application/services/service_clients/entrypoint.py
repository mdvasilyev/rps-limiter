from .base import BaseServiceClient


class EntrypointClient(BaseServiceClient):
    async def get_metrics(self) -> str:
        return await self._request(
            method="GET",
            path="/metrics",
        )
