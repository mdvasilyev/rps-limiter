from typing import AsyncIterator

from dishka import Provider, Scope, provide
from httpx import AsyncClient


class HTTPXProvider(Provider):
    @provide(scope=Scope.APP)
    async def new_connection(self) -> AsyncIterator[AsyncClient]:
        conn = AsyncClient()
        yield conn
        await conn.aclose()
