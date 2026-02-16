from abc import ABC, abstractmethod

from httpx import Response

from src.domain.dto import ModelDTO, RunningModelsQuery


class IModelRegistryClient(ABC):
    @abstractmethod
    async def find_running_models(
        self,
        query: RunningModelsQuery,
    ) -> Response:
        pass

    @abstractmethod
    async def find_all_running_models(self) -> list[ModelDTO]:
        pass
