from httpx import AsyncClient, Response


class BaseServiceClient:
    def __init__(
        self,
        base_url: str,
        client: AsyncClient,
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
    ) -> Response:
        url = f"{self._base_url}/{path.lstrip('/')}"

        response = await self._client.request(
            method=method,
            url=url,
            timeout=self._timeout,
            **kwargs,
        )

        response.raise_for_status()

        return response
