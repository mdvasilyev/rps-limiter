from abc import ABC, abstractmethod


class INotificatorClient(ABC):
    @abstractmethod
    async def notify(self, model_id: str, user_id: str, payload: dict) -> None:
        pass
