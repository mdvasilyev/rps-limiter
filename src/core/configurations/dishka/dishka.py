from dishka import Provider, Scope, make_container

from src.application.services import DecisionMaker, ModelLoadMonitorProvider
from src.application.services.service_clients import (
    BookingClientProvider,
    ModelDispatcherClientProvider,
    ModelRegistryClientProvider,
    NotificatorClientProvider,
    PrometheusClientProvider,
)
from src.core.configurations.config import ConfigProvider
from src.core.configurations.httpx import HTTPXProvider
from src.core.configurations.rabbit import RabbitmqProvider

service_provider = Provider(scope=Scope.APP)
service_provider.provide(DecisionMaker)

container = make_container(
    service_provider,
    ConfigProvider(),
    RabbitmqProvider(),
    HTTPXProvider(),
    PrometheusClientProvider(),
    BookingClientProvider(),
    ModelDispatcherClientProvider(),
    ModelRegistryClientProvider(),
    NotificatorClientProvider(),
    ModelLoadMonitorProvider(),
)
