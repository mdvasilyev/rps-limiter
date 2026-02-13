from abc import ABC, abstractmethod

from src.domain.dto import ModelInfo, Scale, Unbook, WarnUnbooking


class IDecisionMaker(ABC):
    @abstractmethod
    def process(
        self,
        active_models: list[ModelInfo],
        rps_by_model: dict[str, float],
        increase_by_model: dict[str, float],
    ) -> list[Scale | WarnUnbooking | Unbook]:
        pass
