from abc import ABC, abstractmethod

from src.domain.dto import ModelDTO, ModelRpsIncreaseDTO, Scale, Unbook


class IDecisionMaker(ABC):
    @abstractmethod
    def process(
        self,
        active_models: list[ModelDTO],
        metrics: list[ModelRpsIncreaseDTO],
    ) -> list[Scale | Unbook]:
        pass
