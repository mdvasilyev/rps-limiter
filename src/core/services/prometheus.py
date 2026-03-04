import httpx
from httpx import HTTPStatusError, RequestError
from loguru import logger
from pydantic import ValidationError

from src.core.services.base import BaseServiceClient
from src.domain.dto.metric import MetricDTO
from src.domain.exceptions import PrometheusError
from src.domain.interfaces.services import IPrometheus


class PrometheusClient(BaseServiceClient, IPrometheus):
    def __init__(
        self, base_url: str, client: httpx.AsyncClient, timeout: float = 5.0
    ) -> None:
        super().__init__(base_url, client, timeout)
        self._url_path = f"{base_url}/api/v1/query"

    async def query_vector(self, promql_query: str) -> list[MetricDTO]:
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
                    "Prometheus returned non-success status",
                    query=promql_query,
                    status_code=response.status_code,
                    details=str(payload.get("error") or payload.get("status")),
                )

            results = payload.get("data", {}).get("result", [])
            return [MetricDTO.model_validate(r) for r in results]

        except (RequestError, HTTPStatusError) as exc:
            logger.exception(f"HTTP error while querying Prometheus: {exc}")
            status_code = (
                exc.response.status_code
                if isinstance(exc, HTTPStatusError) and exc.response is not None
                else None
            )
            raise PrometheusError(
                "Network or HTTP error while querying Prometheus",
                query=promql_query,
                status_code=status_code,
                details=str(exc),
            ) from exc
        except ValidationError as exc:
            logger.exception(f"Prometheus response schema mismatch: {exc}")
            raise PrometheusError(
                "Prometheus response validation failed",
                query=promql_query,
                details=str(exc),
            ) from exc
        except ValueError as exc:
            logger.exception("Failed to parse Prometheus response")
            raise PrometheusError(
                "Invalid JSON in Prometheus response",
                query=promql_query,
                details=str(exc),
            ) from exc
