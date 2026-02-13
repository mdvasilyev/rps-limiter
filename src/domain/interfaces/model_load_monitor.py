from abc import ABC, abstractmethod

from src.domain.dto import ModelIncreaseDTO, ModelRpsDTO


class IModelLoadMonitor(ABC):
    @abstractmethod
    async def get_current_rps_per_model(self, period_min: int) -> list[ModelRpsDTO]:
        pass

    @abstractmethod
    async def get_increase_per_model(
        self,
        period_min: int,
    ) -> list[ModelIncreaseDTO]:
        pass
