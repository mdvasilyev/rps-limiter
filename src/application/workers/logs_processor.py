from datetime import datetime, timedelta

from httpx import ConnectError
from loguru import logger

from src.domain.dto import (
    FetchAndProcessLogsEvent,
    ModelIncreaseDTO,
    ModelInfo,
    ModelRpsDTO,
    Reservation,
    Scale,
    Unbook,
    WarnUnbooking,
)
from src.domain.interfaces import IDecisionMaker, IModelLoadMonitor
from src.domain.interfaces.service_clients import (
    IBookingClient,
    IModelDispatcherClient,
    IModelRegistryClient,
    INotificatorClient,
)


class LogsProcessorWorker:
    def __init__(
        self,
        booking_client: IBookingClient,
        model_registry_client: IModelRegistryClient,
        model_dispatcher_client: IModelDispatcherClient,
        notificator_client: INotificatorClient,
        model_load_monitor: IModelLoadMonitor,
        decision_maker: IDecisionMaker,
        rps_interval: int,
        increase_interval: int,
        unbooking_strategy: str,
    ):
        self._booking_client = booking_client
        self._model_registry_client = model_registry_client
        self._model_dispatcher_client = model_dispatcher_client
        self._notificator_client = notificator_client
        self._model_load_monitor = model_load_monitor
        self._decision_maker = decision_maker
        self._rps_interval = rps_interval
        self._increase_interval = increase_interval
        self._unbooking_strategy = unbooking_strategy

    async def handle_logs_signal(self, event: FetchAndProcessLogsEvent):
        logger.info(
            "Received metrics evaluation signal at {}",
            event.triggered_at,
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

        try:
            rps_stats: list[ModelRpsDTO] = (
                await self._model_load_monitor.get_current_rps_per_model(
                    self._rps_interval
                )
            )
            increase_stats: list[ModelIncreaseDTO] = (
                await self._model_load_monitor.get_increase_per_model(
                    self._increase_interval
                )
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
                    reservations: list[Reservation]

                    if self._unbooking_strategy == "ALL":
                        reservations = await self._booking_client.get_reservations(
                            model_name=model_name, user_id=user_id
                        )
                    else:
                        min_start_time = datetime.utcnow() - timedelta(
                            hours=self._increase_interval
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
