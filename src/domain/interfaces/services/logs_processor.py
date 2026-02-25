from abc import ABC, abstractmethod

from src.domain.dto.events import FetchAndProcessLogsEvent


class ILogsProcessor(ABC):
    @abstractmethod
    async def handle_logs_signal(self, event: FetchAndProcessLogsEvent) -> None:
        pass
