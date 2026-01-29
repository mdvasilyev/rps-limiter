from dishka import Provider, Scope, make_container

from src.core.configurations.config import ConfigProvider

service_provider = Provider(scope=Scope.APP)

container = make_container(service_provider, ConfigProvider())
