from abc import ABC, abstractmethod

from httpx import Response

from src.domain.dto import ModelInfo


class IModelRegistryClient(ABC):
    @abstractmethod
    async def find_running_models(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        sort: str | None = None,
        filters: dict | None = None,
    ) -> Response:
        pass

    @abstractmethod
    async def find_all_running_models(self) -> list[ModelInfo]:
        pass
