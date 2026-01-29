from typing import Any

import httpx


class BaseServiceClient:
    def __init__(
        self,
        base_url: str,
        client: httpx.AsyncClient,
        timeout: float = 5.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = client
        self._timeout = timeout

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> Any:
        url = f"{self._base_url}{path}"

        response = await self._client.request(
            method=method,
            url=url,
            timeout=self._timeout,
            **kwargs,
        )

        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return response.json()

        return response.text
