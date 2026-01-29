from dishka import Provider, Scope, provide
from faststream.rabbit import RabbitBroker

from src.core.configurations.config import GlobalConfig


class RabbitmqProvider(Provider):
    @provide(scope=Scope.APP)
    def rabbitmq_connection(self, config: GlobalConfig) -> RabbitBroker:
        return RabbitBroker(config.rabbitmq.url)
