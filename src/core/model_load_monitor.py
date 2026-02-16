from loguru import logger

from src.domain.dto import Metric, ModelIncreaseDTO, ModelRpsDTO
from src.domain.exceptions import PrometheusError
from src.domain.interfaces import IModelLoadMonitor
from src.domain.interfaces.service_clients import IPrometheusClient


class ModelLoadMonitor(IModelLoadMonitor):
    def __init__(self, prom_client: IPrometheusClient, service_name: str) -> None:
        self._client = prom_client
        self._service_name = service_name

    async def get_current_rps_per_model(self, period_min: int) -> list[ModelRpsDTO]:
        if period_min <= 0:
            raise ValueError(f"Period must be positive: {period_min}")

        query = (
            f"sum by (model_name) ("
            f'  rate(model_calls_total{{service_name="{self._service_name}"}}[{period_min}m])'
            f")"
        )

        try:
            results: list[Metric] = await self._client.query_vector(query)
        except PrometheusError:
            return []

        parsed_metrics = []
        for res in results:

            model_name: str | None = res.metric.get("model_name")
            if not model_name:
                continue

            try:
                rps = float(res.value.value)
                parsed_metrics.append(ModelRpsDTO(model_name=model_name, rps=rps))
            except (ValueError, TypeError):
                logger.warning(
                    "Could not parse RPS value for model {}: {}",
                    model_name,
                    res.value.value,
                )

        return parsed_metrics

    async def get_increase_per_model(
        self,
        period_min: int,
    ) -> list[ModelIncreaseDTO]:
        if period_min <= 0:
            raise ValueError(f"Period must be positive: {period_min}")

        query = (
            f"sum by (model_name) ("
            f'  increase(model_calls_total{{service_name="{self._service_name}"}}[{period_min}m])'
            f")"
        )

        try:
            results: list[Metric] = await self._client.query_vector(query)
        except PrometheusError:
            return []

        parsed_metrics: list[ModelIncreaseDTO] = []

        for res in results:
            model_name: str | None = res.metric.get("model_name")
            if not model_name:
                continue

            try:
                requests = float(res.value.value)
                parsed_metrics.append(
                    ModelIncreaseDTO(
                        model_name=model_name,
                        requests=requests,
                    )
                )
            except (ValueError, TypeError):
                logger.warning(
                    "Could not parse increase value for model {}: {}",
                    model_name,
                    res.value.value,
                )

        return parsed_metrics
