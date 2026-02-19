from abc import ABC, abstractmethod

from src.domain.dto import NotifyQuery


class INotificator(ABC):
    @abstractmethod
    async def notify(self, query: NotifyQuery) -> str:
        pass
