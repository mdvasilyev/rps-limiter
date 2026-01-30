import asyncio

from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitRouter
from httpx import AsyncClient, ConnectError
from loguru import logger

from src.application.services import DecisionMaker
from src.application.services.model_load_monitor import ModelLoadMonitor
from src.application.services.service_clients import (
    BookingClient,
    ModelDispatcherClient,
    ModelRegistryClient,
    NotificatorClient,
)
from src.core.configurations.config import GlobalConfig
from src.core.configurations.dishka import container
from src.domain.dto import ModelIncreaseDTO, ModelRpsDTO, Scale, Unbook, WarnUnbooking

config = container.get(GlobalConfig)

broker: RabbitBroker = container.get(RabbitBroker)
router: RabbitRouter = RabbitRouter()
broker.include_router(router)


@router.subscriber(config.rabbitmq.logs_queue)
async def handle_logs_signal(message: dict):
    # сага провалилась, что делать
    logger.info(
        "Received metrics evaluation signal at {}",
        message.get("triggered_at"),
    )

    model_registry_client: ModelRegistryClient = container.get(ModelRegistryClient)
    model_dispatcher_client: ModelDispatcherClient = container.get(
        ModelDispatcherClient
    )
    notificator_client: NotificatorClient = container.get(NotificatorClient)
    booking_client: BookingClient = container.get(BookingClient)

    try:
        active_models: list[dict] = (
            await model_registry_client.find_all_running_models()
        )
        if not active_models:
            logger.warning("No active models found")
            return
    except ConnectError as exc:
        logger.error("Connection error while finding all running models: {}", exc)
        return

    model_load_monitor: ModelLoadMonitor = container.get(ModelLoadMonitor)

    period = 1
    try:
        rps_stats: list[ModelRpsDTO] = (
            await model_load_monitor.get_current_rps_per_model(period)
        )
        increase_stats: list[ModelIncreaseDTO] = (
            await model_load_monitor.get_increase_per_model(period)
        )
    except ConnectError as exc:
        logger.error("Connection error while getting rps data: {}", exc)
        return

    rps_by_model: dict[str, float] = {m.model_name: m.rps for m in rps_stats}
    increase_by_model: dict[str, float] = {
        m.model_name: m.requests for m in increase_stats
    }

    decision_maker: DecisionMaker = container.get(DecisionMaker)

    actions: list[Scale | WarnUnbooking | Unbook] = decision_maker.process(
        active_models=active_models,
        rps_by_model=rps_by_model,
        increase_by_model=increase_by_model,
    )

    if not actions:
        logger.info("No actions required")
        return

    for action in actions:
        match action:
            case Scale(model_id, replicas):
                logger.info("Scaling {}", model_id)
                await model_dispatcher_client.scale(model_id, replicas)

            case WarnUnbooking(model_id, user_id):
                logger.info("Warn unbooking {}", model_id)
                await notificator_client.notify(
                    model_id, user_id, {"warning unbooking": model_id}
                )

            case Unbook(model_id, model_name, user_id):
                reservations: dict = await booking_client.get_reservations(
                    model_name=model_name, user_id=user_id
                )
                reservation_id: str = reservations.get("id")
                logger.info("Unbooking {}", reservation_id)
                await booking_client.delete_reservation(reservation_id)
                await notificator_client.notify(
                    model_id, user_id, {"unbooking": model_id}
                )


async def main():
    app = FastStream(broker)
    try:
        await app.run()
    finally:
        logger.info("Closing AsyncClient")
        await container.get(AsyncClient).aclose()

        logger.info("Closing container")
        container.close()


if __name__ == "__main__":
    asyncio.run(main())
