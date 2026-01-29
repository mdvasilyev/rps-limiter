from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class ModelRpsDTO:
    model_name: str
    rps: float
