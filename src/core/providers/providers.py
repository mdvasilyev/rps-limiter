from typing import AsyncIterable

from dishka import Provider, Scope, from_context, provide
from faststream.rabbit import RabbitBroker, RabbitExchange
from httpx import AsyncClient

from src.application.services import DecisionMaker, Publisher
from src.application.workers import LogsProcessorWorker
from src.core.broker import get_rabbitmq_broker, get_rabbitmq_exchange
from src.core.configurations.config import GlobalConfig
from src.core.database.manager import PostgresConnectionManager
from src.core.database.repositories import RpsDataRepository
from src.core.services import (
    BookingClient,
    ModelDispatcherClient,
    ModelLoadMonitor,
    ModelRegistryClient,
    NotificatorClient,
    PrometheusClient,
)
from src.domain.interfaces.repositories import IRpsDataRepository
from src.domain.interfaces.services import (
    IBooking,
    IDecisionMaker,
    IModelDispatcher,
    IModelLoadMonitor,
    IModelRegistry,
    INotificator,
    IPrometheus,
    IPublisher,
)


class AdaptersProvider(Provider):
    scope = Scope.APP

    @provide(scope=scope)
    def global_config(self) -> GlobalConfig:
        return from_context(provides=GlobalConfig, scope=Scope.APP)

    @provide(scope=scope)
    async def httpx_client(self) -> AsyncIterable[AsyncClient]:
        client = AsyncClient()
        yield client
        await client.aclose()

    @provide(scope=scope)
    def rabbitmq_broker(self, config: GlobalConfig) -> RabbitBroker:
        return get_rabbitmq_broker(config.rabbitmq.url)

    @provide(scope=scope)
    def rabbitmq_exchange(self, config: GlobalConfig) -> RabbitExchange:
        return get_rabbitmq_exchange(config.rabbitmq.exchange)

    @provide(scope=scope)
    def postgres_manager(self, config: GlobalConfig) -> PostgresConnectionManager:
        return PostgresConnectionManager(config.postgres)


class ServiceClientsProvider(Provider):
    scope = Scope.APP

    @provide(scope=scope, provides=IBooking)
    def booking_client(
        self, config: GlobalConfig, client: AsyncClient
    ) -> BookingClient:
        return BookingClient(config.booking.url, client)

    @provide(scope=scope, provides=IModelDispatcher)
    def model_dispatcher_client(
        self, config: GlobalConfig, client: AsyncClient
    ) -> ModelDispatcherClient:
        return ModelDispatcherClient(config.model_dispatcher.url, client)

    @provide(scope=scope, provides=IModelRegistry)
    def model_registry_client(
        self, config: GlobalConfig, client: AsyncClient
    ) -> ModelRegistryClient:
        return ModelRegistryClient(config.model_registry.url, client)

    @provide(scope=scope, provides=INotificator)
    def notificator_client(
        self, config: GlobalConfig, client: AsyncClient
    ) -> NotificatorClient:
        return NotificatorClient(config.notificator.url, client)

    @provide(scope=scope, provides=IPrometheus)
    def prometheus_client(
        self, config: GlobalConfig, client: AsyncClient
    ) -> PrometheusClient:
        return PrometheusClient(config.prometheus.url, client)


class RepositoriesProvider(Provider):
    scope = Scope.APP

    @provide(scope=scope, provides=IRpsDataRepository)
    def rps_data_repository(
        self, connection_manager: PostgresConnectionManager
    ) -> RpsDataRepository:
        return RpsDataRepository(connection_manager)


class ServicesProvider(Provider):
    scope = Scope.APP

    @provide(scope=scope, provides=IDecisionMaker)
    def decision_maker(
        self, config: GlobalConfig, rps_data_repository: IRpsDataRepository
    ) -> DecisionMaker:
        return DecisionMaker(
            rps_data_repository,
            config.worker.rps_threshold,
            config.worker.warn_after_mins,
            config.worker.unbook_after_mins,
        )

    @provide(scope=scope, provides=IModelLoadMonitor)
    def model_load_monitor(self, client: IPrometheus) -> ModelLoadMonitor:
        return ModelLoadMonitor(client, "entrypoint")

    @provide(scope=scope, provides=IPublisher)
    def publisher(
        self, broker: RabbitBroker, exchange: RabbitExchange, config: GlobalConfig
    ) -> Publisher:
        return Publisher(broker, exchange, config.rabbitmq.logs_queue)


class WorkersProvider(Provider):
    scope = Scope.APP

    @provide(scope=scope, provides=LogsProcessorWorker)
    def logs_processor_worker(
        self,
        booking_client: IBooking,
        model_registry_client: IModelRegistry,
        model_dispatcher_client: IModelDispatcher,
        notificator_client: INotificator,
        model_load_monitor: IModelLoadMonitor,
        decision_maker: IDecisionMaker,
        rps_data_repository: IRpsDataRepository,
        config: GlobalConfig,
    ) -> LogsProcessorWorker:
        return LogsProcessorWorker(
            booking_client,
            model_registry_client,
            model_dispatcher_client,
            notificator_client,
            model_load_monitor,
            decision_maker,
            rps_data_repository,
            config.worker.rps_interval,
            config.worker.increase_interval,
            config.worker.unbooking,
        )
