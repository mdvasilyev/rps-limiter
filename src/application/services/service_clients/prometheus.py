import httpx
from dishka import Provider, Scope, provide
from httpx import AsyncClient, HTTPStatusError, RequestError
from loguru import logger
from pydantic import ValidationError

from src.application.services.service_clients.base import BaseServiceClient
from src.core.configurations.config import GlobalConfig
from src.domain.dto import Metric
from src.domain.exceptions.prometheus import PrometheusError


class PrometheusClient(BaseServiceClient):
    def __init__(
        self, base_url: str, client: httpx.AsyncClient, timeout: float = 5.0
    ) -> None:
        super().__init__(base_url, client, timeout)
        self._url_path = f"{base_url}/api/v1/query"

    async def query_vector(self, promql_query: str) -> list[Metric]:
        try:
            params = {"query": promql_query}
            response: httpx.Response = await self._client.get(
                self._url_path, params=params, timeout=self._timeout
            )
            response.raise_for_status()

            payload: dict = response.json()

            if payload.get("status") != "success":
                logger.error("Prometheus API error: {}", payload.get("error"))
                raise PrometheusError(
                    f"Prometheus returned status: {payload.get('status')}"
                )

            results = payload.get("data", {}).get("result", [])
            return [Metric.model_validate(r) for r in results]

        except (RequestError, HTTPStatusError) as exc:
            logger.exception(f"HTTP error while querying Prometheus: {exc}")
            raise PrometheusError(f"Network or HTTP error: {exc}") from exc
        except ValidationError as exc:
            logger.exception(f"Prometheus response schema mismatch: {exc}")
            raise PrometheusError("Response validation failed") from exc
        except ValueError as exc:
            logger.exception("Failed to parse Prometheus response")
            raise PrometheusError("Invalid JSON response") from exc


class PrometheusClientProvider(Provider):
    @provide(scope=Scope.APP)
    def prometheus_client(
        self, config: GlobalConfig, client: AsyncClient
    ) -> PrometheusClient:
        return PrometheusClient(config.prometheus.url, client)
