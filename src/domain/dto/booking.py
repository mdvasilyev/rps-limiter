from dataclasses import dataclass


@dataclass(frozen=True)
class WarnUnbooking:
    model: str
    user_id: str


@dataclass(frozen=True)
class Unbook:
    model_id: str
    model_name: str
    user_id: str
