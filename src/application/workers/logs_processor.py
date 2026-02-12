from datetime import datetime, timedelta

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
    Reservation,
    Scale,
    Unbook,
    WarnUnbooking,
)


class LogsProcessorWorker:
    def __init__(
        self,
        booking_client: BookingClient,
        model_registry_client: ModelRegistryClient,
        model_dispatcher_client: ModelDispatcherClient,
        notificator_client: NotificatorClient,
        model_load_monitor: ModelLoadMonitor,
        config: GlobalConfig,
        decision_maker: DecisionMaker,
    ):
        self._booking_client = booking_client
        self._model_registry_client = model_registry_client
        self._model_dispatcher_client = model_dispatcher_client
        self._notificator_client = notificator_client
        self._model_load_monitor = model_load_monitor
        self._config = config
        self._decision_maker = decision_maker

    async def handle_logs_signal(self, request: dict):
        logger.info(
            "Received metrics evaluation signal at {}",
            request.get("triggered_at"),
        )

        try:
            active_models: list[ModelInfo] = (
                await self._model_registry_client.find_all_running_models()
            )
            if not active_models:
                logger.warning("No active models found")
                return
        except ConnectError as exc:
            logger.error("Connection error while finding all running models: {}", exc)
            return

        rps_interval = self._config.worker.rps_interval
        increase_interval = self._config.worker.increase_interval
        try:
            rps_stats: list[ModelRpsDTO] = (
                await self._model_load_monitor.get_current_rps_per_model(rps_interval)
            )
            increase_stats: list[ModelIncreaseDTO] = (
                await self._model_load_monitor.get_increase_per_model(increase_interval)
            )
        except ConnectError as exc:
            logger.error("Connection error while getting rps data: {}", exc)
            return

        rps_by_model: dict[str, float] = {m.model_name: m.rps for m in rps_stats}
        increase_by_model: dict[str, float] = {
            m.model_name: m.requests for m in increase_stats
        }

        actions: list[Scale | WarnUnbooking | Unbook] = self._decision_maker.process(
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
                    logger.info(
                        "Scaling model_id='{}' to replicas='{}'", model_id, replicas
                    )
                    await self._model_dispatcher_client.scale(model_id, replicas)

                case WarnUnbooking(model_id, user_id):
                    logger.info("Warn unbooking model_id='{}'", model_id)
                    await self._notificator_client.notify(
                        model_id, user_id, {"warning unbooking": model_id}
                    )

                case Unbook(model_id, model_name, user_id):
                    unbooking_strategy = self._config.worker.unbooking
                    reservations: list[Reservation]

                    if unbooking_strategy == "ALL":
                        reservations = await self._booking_client.get_reservations(
                            model_name=model_name, user_id=user_id
                        )
                    else:
                        min_start_time = datetime.utcnow() - timedelta(
                            hours=increase_interval
                        )
                        reservations = await self._booking_client.get_reservations(
                            model_name=model_name,
                            user_id=user_id,
                            min_start_time=str(min_start_time),
                        )

                    for reservation in reservations:
                        reservation_id: str = reservation.id
                        logger.info("Unbooking reservation_id='{}'", reservation_id)
                        await self._booking_client.delete_reservation(reservation_id)
                        await self._notificator_client.notify(
                            model_id, user_id, {"unbooking": model_id}
                        )
