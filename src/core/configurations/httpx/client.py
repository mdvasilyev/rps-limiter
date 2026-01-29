from dishka import Provider, Scope, provide
from httpx import AsyncClient


class HTTPXProvider(Provider):
    @provide(scope=Scope.APP)
    def new_connection(self) -> AsyncClient:
        return AsyncClient()
