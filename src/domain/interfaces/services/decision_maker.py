from abc import ABC, abstractmethod

from src.domain.dto.booking import UnbookAction
from src.domain.dto.model import ModelDTO, ModelRpsIncreaseDTO, ScaleAction


class IDecisionMaker(ABC):
    @abstractmethod
    def process(
        self,
        active_models: list[ModelDTO],
        metrics: list[ModelRpsIncreaseDTO],
    ) -> list[ScaleAction | UnbookAction]:
        pass
