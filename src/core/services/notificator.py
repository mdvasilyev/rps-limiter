from src.core.services.base import BaseServiceClient
from src.domain.dto.notificator import NotifyQuery
from src.domain.interfaces.services import INotificator


class NotificatorClient(BaseServiceClient, INotificator):
    async def notify(self, query: NotifyQuery) -> str:
        pass
