from abc import ABC, abstractmethod

from src.domain.dto import ModelDTO, Scale, Unbook, WarnUnbooking


class IDecisionMaker(ABC):
    @abstractmethod
    def process(
        self,
        active_models: list[ModelDTO],
        rps_by_model: dict[str, float],
        increase_by_model: dict[str, float],
    ) -> list[Scale | WarnUnbooking | Unbook]:
        pass
