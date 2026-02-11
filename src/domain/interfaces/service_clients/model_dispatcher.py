from abc import ABC, abstractmethod


class IModelDispatcherClient(ABC):
    @abstractmethod
    async def uninstall(self, *, model_id: str) -> dict:
        pass

    async def scale(self, model_id: str, replicas: int) -> dict:
        pass

    async def saga_status(self, saga_id: str) -> dict:
        pass
