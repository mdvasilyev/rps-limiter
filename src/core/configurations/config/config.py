from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    host: str
    port: int


class LoggingConfig(BaseModel):
    level: str
    json: bool
    service_name: str


class PostgresConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    db: str


class WorkerSettings(BaseModel):
    process_interval: int
    rps_interval: int
    increase_interval: int
    unbooking: Literal["ALL", "IN_ROW"]
    rps_threshold: float
    warn_after_mins: int
    unbook_after_mins: int


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

    app: AppConfig
    logging: LoggingConfig
    postgres: PostgresConfig
    worker: WorkerSettings
    rabbitmq: RabbitMQConfig
    model_registry: ModelRegistryConfig
    model_dispatcher: ModelDispatcherConfig
    booking: BookingServiceConfig
    prometheus: PrometheusConfig
    notificator: NotificatorConfig
