from abc import ABC, abstractmethod

from src.domain.dto.booking import UnbookAction
from src.domain.dto.model import ModelDTO, ModelRpsIncreaseDTO, ScaleAction
from src.domain.dto.notificator import WarnUnbookingAction


class IDecisionMaker(ABC):
    @abstractmethod
    async def process(
        self,
        increase_interval: int,
        active_models: list[ModelDTO],
        metrics: list[ModelRpsIncreaseDTO],
    ) -> list[ScaleAction | UnbookAction | WarnUnbookingAction]:
        pass
