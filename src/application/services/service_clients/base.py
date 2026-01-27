from typing import Any

import aiohttp


class BaseServiceClient:
    def __init__(
        self,
        base_url: str,
        session: aiohttp.ClientSession,
        timeout: int = 5,
    ):
        self._base_url = base_url.rstrip("/")
        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> Any:
        url = f"{self._base_url}{path}"

        async with self._session.request(
            method=method,
            url=url,
            timeout=self._timeout,
            **kwargs,
        ) as response:
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return await response.json()

            return await response.text()
