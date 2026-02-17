from abc import ABC, abstractmethod

from src.domain.dto import FetchAndProcessLogsEvent


class ILogsProcessorWorker(ABC):
    @abstractmethod
    async def handle_logs_signal(self, event: FetchAndProcessLogsEvent) -> None:
        pass
