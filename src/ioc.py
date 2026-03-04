from dishka import AsyncContainer, make_async_container

from src.core.configurations.config import GlobalConfig
from src.core.providers import (
    AdaptersProvider,
    RepositoriesProvider,
    ServiceClientsProvider,
    ServicesProvider,
    WorkersProvider,
)


def create_container() -> AsyncContainer:
    return make_async_container(
        AdaptersProvider(),
        ServiceClientsProvider(),
        RepositoriesProvider(),
        ServicesProvider(),
        WorkersProvider(),
        context={
            GlobalConfig: GlobalConfig(),  # type: ignore[call-arg]
        },
    )
