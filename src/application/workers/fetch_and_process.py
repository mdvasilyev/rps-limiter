import asyncio

from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitRouter
from loguru import logger

from src.application.services import (
    DecisionMaker,
    ScaleDown,
    ScaleUp,
    Unbook,
    WarnUnbooking,
)
from src.application.services.model_load_monitor import ModelLoadMonitor
from src.application.services.service_clients import (
    BookingClient,
    ModelDispatcherClient,
    ModelRegistryClient,
    NotificatorClient,
)
from src.application.services.service_clients.prometheus import PrometheusClient
from src.core.configurations.config import GlobalConfig
from src.core.configurations.dishka import container

config = container.get(GlobalConfig)

broker: RabbitBroker = container.get(RabbitBroker)
app = FastStream(broker)
router = RabbitRouter()
broker.include_router(router)


@router.subscriber(config.rabbitmq.logs_queue)
async def handle_logs_signal(message: dict):
    # сага провалилась, что делать
    logger.info(
        "Received metrics evaluation signal at {}",
        message.get("triggered_at"),
    )

    model_registry_client = container.get(ModelRegistryClient)
    prometheus_client = container.get(PrometheusClient)
    model_dispatcher_client = container.get(ModelDispatcherClient)
    notificator_client = container.get(NotificatorClient)
    booking_client = container.get(BookingClient)

    active_models = await model_registry_client.find_running_models()
    if not active_models:
        logger.warning("No active models found")
        return

    # async with PrometheusClient(base_url="") as prom_client:
    #     monitor = ModelLoadMonitor(prom_client=prom_client, service_name="")
    #     logger.info("Checking metrics...")
    #     stats = await monitor.get_current_rps_per_model(1)
    rps_stats = await prometheus_client.get_rps_per_model()
    increase_stats = await prometheus_client.get_increase_per_model()

    rps_by_model = {m.model_name: m.rps for m in rps_stats}
    increase_by_model = {m.model_name: m.requests for m in increase_stats}

    decision_maker = container.get(DecisionMaker)

    actions = decision_maker.process(
        active_models=active_models,
        rps_by_model=rps_by_model,
        increase_by_model=increase_by_model,
    )

    if not actions:
        logger.info("No actions required")
        return

    for action in actions:
        match action:
            case ScaleUp(model):
                logger.info("Scaling UP {}", model)
                await model_dispatcher_client.scale_up(model)

            case ScaleDown(model):
                logger.info("Scaling DOWN {}", model)
                await model_dispatcher_client.scale_down(model)

            case WarnUnbooking(model):
                logger.warning("Warn unbooking {}", model)
                await notificator_client.warn_unbooking(model)

            case Unbook(model):
                logger.warning("Unbooking {}", model)
                await booking_client.unbook_all(model)
                await notificator_client.notify_unbook(model)


async def main():
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
