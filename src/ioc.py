from dishka import AsyncContainer, make_async_container

from src.core import (
    AdaptersProvider,
    ServiceClientsProvider,
    ServicesProvider,
    WorkersProvider,
)
from src.core.configurations.config import GlobalConfig


def create_container() -> AsyncContainer:
    return make_async_container(
        AdaptersProvider(),
        ServiceClientsProvider(),
        ServicesProvider(),
        WorkersProvider(),
        context={
            GlobalConfig: GlobalConfig(),
        },
    )
