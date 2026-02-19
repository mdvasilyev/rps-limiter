from abc import ABC, abstractmethod


class IPublisher(ABC):
    @abstractmethod
    def start(self, interval: int) -> None:
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass
