from abc import ABC, abstractmethod

from src.domain.dto import SagaQuery, ScaleQuery, UninstallQuery


class IModelDispatcherClient(ABC):
    @abstractmethod
    async def uninstall(self, query: UninstallQuery) -> dict:
        pass

    async def scale(self, query: ScaleQuery) -> dict:
        pass

    async def saga_status(self, query: SagaQuery) -> dict:
        pass
