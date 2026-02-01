from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True)
class WarnUnbooking:
    model: str
    user_id: str


@dataclass(frozen=True)
class Unbook:
    model_id: str
    model_name: str
    user_id: str


@dataclass(frozen=True)
class User:
    id: str
    name: str


@dataclass(frozen=True)
class Slot:
    start: int
    end: int
    id: str


class Reservation(BaseModel):
    id: str
    user: User
    model_name: str
    config_id: int
    model_id: str
    slots: list[Slot]
