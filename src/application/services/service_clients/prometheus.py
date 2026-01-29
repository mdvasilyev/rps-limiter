from dataclasses import dataclass
from typing import NamedTuple, Self

import httpx
from httpx import AsyncClient, HTTPStatusError, RequestError
from loguru import logger
from pydantic import BaseModel, ValidationError

from src.domain.exceptions.prometheus import PrometheusError


@dataclass(frozen=True, kw_only=True)
class ModelRpsDTO:
    model_name: str
    rps: float


class MetricValue(NamedTuple):
    timestamp: float
    value: str


class Metric(BaseModel):
    metric: dict[str, str]
    value: MetricValue


class PrometheusClient:
    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        self._base_url = base_url
        self._timeout = timeout
        self._url_path = "/api/v1/query"
        self._client: AsyncClient | None = None

    async def __aenter__(self) -> Self:
        self._client = AsyncClient(base_url=self._base_url, timeout=self._timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client:
            await self._client.aclose()

    async def query_vector(self, promql_query: str) -> list[Metric]:
        if self._client is None:
            raise PrometheusError(
                "Client not initialized. Use 'async with' context manager."
            )

        try:
            params = {"query": promql_query}
            response: httpx.Response = await self._client.get(
                self._url_path, params=params
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


