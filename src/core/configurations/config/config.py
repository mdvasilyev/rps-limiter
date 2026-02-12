from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseModel):
    process_interval: int
    rps_interval: int
    increase_interval: int
    unbooking: Literal["ALL", "IN_ROW"]


class RabbitMQConfig(BaseModel):
    url: str
    exchange: str
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


class GlobalConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    worker: WorkerSettings
    rabbitmq: RabbitMQConfig
    model_registry: ModelRegistryConfig
    model_dispatcher: ModelDispatcherConfig
    booking: BookingServiceConfig
    prometheus: PrometheusConfig
    notificator: NotificatorConfig
