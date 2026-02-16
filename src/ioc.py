from dishka import AsyncContainer, make_async_container
from httpx import AsyncClient

from src.core import (
    AdaptersProvider,
    ServiceClientsProvider,
    ServicesProvider,
    WorkersProvider,
)
from src.core.configurations.config import GlobalConfig


def create_container() -> AsyncContainer:
    config = GlobalConfig()
    httpx_client = AsyncClient()
    return make_async_container(
        AdaptersProvider(),
        ServiceClientsProvider(),
        ServicesProvider(),
        WorkersProvider(),
        context={
            GlobalConfig: config,
            AsyncClient: httpx_client,
        },
    )
