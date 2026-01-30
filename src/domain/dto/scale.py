from dataclasses import dataclass


@dataclass(frozen=True)
class ScaleUp:
    model: str


@dataclass(frozen=True)
class ScaleDown:
    model: str
