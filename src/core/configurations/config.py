from functools import lru_cache

import yaml
from pydantic import BaseModel, ValidationError


class AppConfig(BaseModel):
    host: str
    port: int


class DBConfig(BaseModel):
    host: str
    port: int
    name: str
    user: str
    password: str
    pool_size: int


class WorkerSettings(BaseModel):
    interval: int


class GlobalConfig(BaseModel):
    app: AppConfig
    db: DBConfig
    worker: WorkerSettings

    @classmethod
    def load(cls, file_path: str = "config.yaml") -> "GlobalConfig":
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
            return cls(**data)
        except FileNotFoundError:
            raise RuntimeError(f"Configuration file '{file_path}' not found.")
        except ValidationError as e:
            raise RuntimeError(f"Invalid configuration:\n{e}")


@lru_cache(maxsize=1)
def get_config() -> GlobalConfig:
    return GlobalConfig.load()
