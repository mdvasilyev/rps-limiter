from dishka import (
    AsyncContainer,
    Provider,
    Scope,
    from_context,
    make_async_container,
    provide,
)
from faststream.rabbit import RabbitBroker, RabbitExchange
from httpx import AsyncClient

from src.application.services import DecisionMaker, ModelLoadMonitor, SignalPublisher
from src.application.services.service_clients import (
    BookingClient,
    ModelDispatcherClient,
    ModelRegistryClient,
    NotificatorClient,
    PrometheusClient,
)
from src.application.workers import LogsProcessorWorker
from src.core import get_rabbitmq_broker, get_rabbitmq_exchange
from src.core.configurations.config import GlobalConfig
from src.domain.interfaces.service_clients import (
    IBookingClient,
    IModelDispatcherClient,
    IModelRegistryClient,
    INotificatorClient,
    IPrometheusClient,
)


class AdaptersProvider(Provider):
    scope = Scope.APP

    @provide(scope=scope)
    def global_config(self) -> GlobalConfig:
        return from_context(provides=GlobalConfig, scope=Scope.APP)

    @provide(scope=scope)
    def httpx_client(self) -> AsyncClient:
        return from_context(provides=AsyncClient, scope=Scope.APP)

    @provide(scope=scope)
    def rabbitmq_broker(self, config: GlobalConfig) -> RabbitBroker:
        return get_rabbitmq_broker(config.rabbitmq.url)

    @provide(scope=scope)
    def rabbitmq_exchange(self, config: GlobalConfig) -> RabbitExchange:
        return get_rabbitmq_exchange(config.rabbitmq.exchange)


class ServiceClientsProvider(Provider):
    scope = Scope.APP

    @provide(scope=scope, provides=IBookingClient)
    def booking_client(
        self, config: GlobalConfig, client: AsyncClient
    ) -> BookingClient:
        return BookingClient(config.booking.url, client)

    @provide(scope=scope, provides=IModelDispatcherClient)
    def model_dispatcher_client(
        self, config: GlobalConfig, client: AsyncClient
    ) -> ModelDispatcherClient:
        return ModelDispatcherClient(config.model_dispatcher.url, client)

    @provide(scope=scope, provides=IModelRegistryClient)
    def model_registry_client(
        self, config: GlobalConfig, client: AsyncClient
    ) -> ModelRegistryClient:
        return ModelRegistryClient(config.model_registry.url, client)

    @provide(scope=scope, provides=INotificatorClient)
    def notificator_client(
        self, config: GlobalConfig, client: AsyncClient
    ) -> NotificatorClient:
        return NotificatorClient(config.notificator.url, client)

    @provide(scope=scope, provides=IPrometheusClient)
    def prometheus_client(
        self, config: GlobalConfig, client: AsyncClient
    ) -> PrometheusClient:
        return PrometheusClient(config.prometheus.url, client)


class ServicesProvider(Provider):
    scope = Scope.APP

    @provide(scope=scope)
    def decision_maker(self) -> DecisionMaker:
        return DecisionMaker()

    @provide(scope=scope)
    def model_load_monitor(self, client: PrometheusClient) -> ModelLoadMonitor:
        return ModelLoadMonitor(client, "entrypoint")

    @provide(scope=scope)
    def sigal_publisher(
        self, broker: RabbitBroker, config: GlobalConfig
    ) -> SignalPublisher:
        return SignalPublisher(broker, config.rabbitmq.logs_queue)


class WorkersProvider(Provider):
    scope = Scope.APP

    @provide(scope=scope)
    def logs_processor_worker(
        self,
        booking_client: BookingClient,
        model_registry_client: ModelRegistryClient,
        model_dispatcher_client: ModelDispatcherClient,
        notificator_client: NotificatorClient,
        model_load_monitor: ModelLoadMonitor,
        config: GlobalConfig,
        decision_maker: DecisionMaker,
    ) -> LogsProcessorWorker:
        return LogsProcessorWorker(
            booking_client,
            model_registry_client,
            model_dispatcher_client,
            notificator_client,
            model_load_monitor,
            decision_maker,
            config.worker.rps_interval,
            config.worker.increase_interval,
            config.worker.unbooking,
        )


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
