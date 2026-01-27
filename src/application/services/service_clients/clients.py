import aiohttp

from .booking import BookingClient
from .entrypoint import EntrypointClient
from .model_dispatcher import ModelDispatcherClient
from .model_registry import ModelRegistryClient
from .notificator import NotificatorClient


class ServiceClients:
    def __init__(self, config, session: aiohttp.ClientSession):
        self._config = config
        self._session = session  # session создаём в main и передаём сюда

        # Инициализируем клиентов сразу
        self.model_registry: ModelRegistryClient = ModelRegistryClient(
            self._config.model_registry.url,
            session=self._session,
        )
        self.model_dispatcher: ModelDispatcherClient = ModelDispatcherClient(
            self._config.model_dispatcher.url,
            session=self._session,
        )
        self.booking: BookingClient = BookingClient(
            self._config.booking.url,
            session=self._session,
        )
        self.entrypoint: EntrypointClient = EntrypointClient(
            self._config.entrypoint.url,
            session=self._session,
        )
        self.notificator: NotificatorClient = NotificatorClient(
            self._config.notificator.url,
            session=self._session,
        )

    async def close(self) -> None:
        if self._session:
            await self._session.close()
