from enum import Enum


class Event(str, Enum):
    LOGS = "logs"

    @property
    def process(self) -> str:
        return f"{self.value}.process"
