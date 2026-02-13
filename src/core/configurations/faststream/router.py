from dishka.integrations.faststream import inject
from faststream.rabbit import RabbitExchange, RabbitRouter

from src.application.workers import LogsProcessorWorker
from src.domain.events import Event


def create_router(exchange: RabbitExchange) -> RabbitRouter:
    router = RabbitRouter()

    @router.subscriber(Event.LOGS.process, exchange=exchange)
    @inject
    async def process_logs(request: dict, worker: LogsProcessorWorker) -> None:
        await worker.handle_logs_signal(request)

    return router
