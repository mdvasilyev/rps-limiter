from abc import ABC, abstractmethod

from src.domain.dto.model import ModelDTO, RunningModelsQuery


class IModelRegistry(ABC):
    @abstractmethod
    async def find_running_models(
        self,
        query: RunningModelsQuery,
    ) -> list[ModelDTO]:
        pass

    @abstractmethod
    async def find_all_running_models(self) -> list[ModelDTO]:
        pass
