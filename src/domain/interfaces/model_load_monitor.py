from abc import ABC, abstractmethod

from src.domain.dto import ModelIncreaseDTO, ModelRpsDTO, ModelRpsIncreaseDTO


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

    @abstractmethod
    async def get_rps_and_increase_per_model(
        self,
        rps_period_min: int,
        increase_period_min: int,
    ) -> list[ModelRpsIncreaseDTO]:
        pass
