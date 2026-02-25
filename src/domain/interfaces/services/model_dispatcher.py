from abc import ABC, abstractmethod

from src.domain.dto.model import ScaleQuery, UninstallQuery
from src.domain.dto.saga import SagaDTO, SagaQuery


class IModelDispatcher(ABC):
    @abstractmethod
    async def uninstall(self, query: UninstallQuery) -> SagaDTO:
        pass

    async def scale(self, query: ScaleQuery) -> SagaDTO:
        pass

    async def saga_status(self, query: SagaQuery) -> SagaDTO:
        pass
