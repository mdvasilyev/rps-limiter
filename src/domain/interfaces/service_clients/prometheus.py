from abc import ABC, abstractmethod

from src.domain.dto import Metric


class IPrometheusClient(ABC):
    @abstractmethod
    async def query_vector(self, promql_query: str) -> list[Metric]:
        pass
