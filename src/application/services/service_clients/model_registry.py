from .base import BaseServiceClient


class ModelRegistryClient(BaseServiceClient):
    async def find_running_models(self, payload: dict) -> dict:
        return await self._request(
            method="POST",
            path="/v2/models/running/find-by",
            json=payload,
        )
