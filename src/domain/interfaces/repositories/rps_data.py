from abc import ABC, abstractmethod

from src.domain.dto.rps_data import (
    DeleteIdleModelQuery,
    GetIdleModelQuery,
    IdleModelDTO,
    PostIdleModelQuery,
)


class IRpsDataRepository(ABC):
    @abstractmethod
    async def get_idle_model(self, query: GetIdleModelQuery) -> IdleModelDTO | None:
        pass

    @abstractmethod
    async def post_idle_model(self, query: PostIdleModelQuery) -> IdleModelDTO:
        pass

    @abstractmethod
    async def delete_idle_model(self, query: DeleteIdleModelQuery) -> dict[str, str]:
        pass
