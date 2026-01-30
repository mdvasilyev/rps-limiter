from dataclasses import dataclass


@dataclass(frozen=True)
class WarnUnbooking:
    model: str


@dataclass(frozen=True)
class Unbook:
    model: str
