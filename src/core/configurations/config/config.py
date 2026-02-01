from typing import Literal

import yaml
from dishka import Provider, Scope, provide
from pydantic import BaseModel, ValidationError


class WorkerSettings(BaseModel):
    process_interval: int
    rps_interval: int
    increase_interval: int
    unbooking: Literal["ALL", "IN_ROW"]


class RabbitMQConfig(BaseModel):
    url: str
    logs_queue: str


class ModelRegistryConfig(BaseModel):
    url: str


class ModelDispatcherConfig(BaseModel):
    url: str


class BookingServiceConfig(BaseModel):
    url: str


class PrometheusConfig(BaseModel):
    url: str


class NotificatorConfig(BaseModel):
    url: str


class GlobalConfig(BaseModel):
    worker: WorkerSettings
    rabbitmq: RabbitMQConfig

    model_registry: ModelRegistryConfig
    model_dispatcher: ModelDispatcherConfig
    booking: BookingServiceConfig
    prometheus: PrometheusConfig
    notificator: NotificatorConfig


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    def global_config(self) -> GlobalConfig:
        file_path: str = "config.yaml"
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
            return GlobalConfig(**data)
        except FileNotFoundError:
            raise RuntimeError(f"Configuration file '{file_path}' not found.")
        except ValidationError as e:
            raise RuntimeError(f"Invalid configuration:\n{e}")
