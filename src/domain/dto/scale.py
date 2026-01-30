from dataclasses import dataclass


@dataclass(frozen=True)
class Scale:
    model_id: str
    replicas: int
