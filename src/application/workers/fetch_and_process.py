from dishka import AsyncContainer
from httpx import ConnectError
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
from src.domain.dto import (
    ModelIncreaseDTO,
    ModelInfo,
    ModelRpsDTO,
    Scale,
    Unbook,
    WarnUnbooking,
)


async def handle_logs_signal(message: dict, container: AsyncContainer):
    # сага провалилась, что делать
    logger.info(
        "Received metrics evaluation signal at {}",
        message.get("triggered_at"),
    )

    model_registry_client = await container.get(ModelRegistryClient)
    model_dispatcher_client = await container.get(ModelDispatcherClient)
    notificator_client = await container.get(NotificatorClient)
    booking_client = await container.get(BookingClient)

    try:
        active_models: list[ModelInfo] = (
            await model_registry_client.find_all_running_models()
        )
        if not active_models:
            logger.warning("No active models found")
            return
    except ConnectError as exc:
        logger.error("Connection error while finding all running models: {}", exc)
        return

    model_load_monitor = await container.get(ModelLoadMonitor)

    config = await container.get(GlobalConfig)
    rps_interval = config.worker.rps_interval
    increase_interval = config.worker.increase_interval
    try:
        rps_stats: list[ModelRpsDTO] = (
            await model_load_monitor.get_current_rps_per_model(rps_interval)
        )
        increase_stats: list[ModelIncreaseDTO] = (
            await model_load_monitor.get_increase_per_model(increase_interval)
        )
    except ConnectError as exc:
        logger.error("Connection error while getting rps data: {}", exc)
        return

    rps_by_model: dict[str, float] = {m.model_name: m.rps for m in rps_stats}
    increase_by_model: dict[str, float] = {
        m.model_name: m.requests for m in increase_stats
    }

    decision_maker = await container.get(DecisionMaker)

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
                # Ограничить интервал времени
                reservations: dict = await booking_client.get_reservations(
                    model_name=model_name, user_id=user_id
                )
                reservation_id: str = reservations.get("id")
                logger.info("Unbooking {}", reservation_id)
                await booking_client.delete_reservation(reservation_id)
                await notificator_client.notify(
                    model_id, user_id, {"unbooking": model_id}
                )
