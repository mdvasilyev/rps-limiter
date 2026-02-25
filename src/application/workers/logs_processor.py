from datetime import UTC, datetime, timedelta
from typing import Literal

from httpx import ConnectError
from loguru import logger

from src.domain.dto import (
    DeleteReservationSlotQuery,
    FetchAndProcessLogsEvent,
    GetReservationsQuery,
    ModelDTO,
    ModelRpsIncreaseDTO,
    ReservationDTO,
    Scale,
    ScaleQuery,
    Unbook,
)
from src.domain.interfaces.services import (
    IBooking,
    IDecisionMaker,
    ILogsProcessor,
    IModelDispatcher,
    IModelLoadMonitor,
    IModelRegistry,
)


class LogsProcessorWorker(ILogsProcessor):
    def __init__(
        self,
        booking_client: IBooking,
        model_registry_client: IModelRegistry,
        model_dispatcher_client: IModelDispatcher,
        model_load_monitor: IModelLoadMonitor,
        decision_maker: IDecisionMaker,
        rps_interval: int,
        increase_interval: int,
        unbooking_strategy: Literal["ALL", "IN_ROW"],
    ):
        self._booking_client = booking_client
        self._model_registry_client = model_registry_client
        self._model_dispatcher_client = model_dispatcher_client
        self._model_load_monitor = model_load_monitor
        self._decision_maker = decision_maker
        self._rps_interval = rps_interval
        self._increase_interval = increase_interval
        self._unbooking_strategy = unbooking_strategy

    async def _get_active_models(self) -> list[ModelDTO] | None:
        try:
            models = await self._model_registry_client.find_all_running_models()
            if not models:
                logger.warning("No active models found")
                return None
            return models
        except ConnectError as exc:
            logger.error("Connection error while finding running models: {}", exc)
            return None

    async def _get_metrics(self) -> list[ModelRpsIncreaseDTO] | None:
        try:
            return await self._model_load_monitor.get_rps_and_increase_per_model(
                rps_period_min=self._rps_interval,
                increase_period_min=self._increase_interval,
            )
        except ConnectError as exc:
            logger.error("Connection error while getting metrics: {}", exc)
            return None

    def _filter_reservations(
        self, reservations: list[ReservationDTO]
    ) -> list[ReservationDTO]:
        if self._unbooking_strategy == "ALL":
            return reservations

        for reservation in reservations:
            if not reservation.slots:
                continue

            sorted_slots = sorted(reservation.slots, key=lambda s: s.start)

            in_row = [sorted_slots[0]]

            for slot in sorted_slots[1:]:
                prev = in_row[-1]

                if prev.end == slot.start:
                    in_row.append(slot)
                else:
                    break

            reservation.slots = in_row

        return reservations

    async def _get_reservations(
        self,
        model_name: str,
        user_id: str,
    ) -> list[ReservationDTO]:
        results: list[ReservationDTO] = []

        min_start_time = datetime.now(UTC) - timedelta(hours=self._increase_interval)
        query = GetReservationsQuery(
            model_name=model_name, user_id=user_id, min_start_time=str(min_start_time)
        )

        while True:
            items = await self._booking_client.get_reservations(query=query)

            if not items:
                break

            results.extend(items)
            query.page += 1

        return self._filter_reservations(results)

    async def _handle_scale(self, model_id: str, replicas: int) -> None:
        try:
            logger.info("Scaling model_id='{}' to replicas='{}'", model_id, replicas)
            await self._model_dispatcher_client.scale(
                query=ScaleQuery(
                    modelId=model_id,
                    replicas=replicas,
                ),
            )
        except ConnectError as exc:
            logger.error("Connection error while scaling model: {}", exc)
            return None

    async def _handle_unbook(
        self,
        model_name: str,
        user_id: str,
    ) -> None:
        reservations = await self._get_reservations(model_name, user_id)

        for reservation in reservations:
            for slot in reservation.slots:
                logger.info(
                    "Unbooking slot_id='{}' for reservation_id='{}'",
                    slot.id,
                    reservation.id,
                )

                await self._booking_client.delete_reservation_slot(
                    query=DeleteReservationSlotQuery(
                        reservation_id=reservation.id, slot_usage_id=slot.id
                    )
                )

    async def _execute_actions(
        self,
        actions: list[Scale | Unbook],
    ) -> None:
        for action in actions:
            match action:
                case Scale(model_id, replicas):
                    await self._handle_scale(model_id, replicas)

                case Unbook(model_name, user_id):
                    await self._handle_unbook(model_name, user_id)

    async def handle_logs_signal(self, event: FetchAndProcessLogsEvent) -> None:
        logger.info(
            "Received {} signal at {}",
            event.type,
            event.triggered_at,
        )

        active_models = await self._get_active_models()
        if not active_models:
            return

        metrics = await self._get_metrics()
        if metrics is None:
            return

        actions = self._decision_maker.process(
            active_models=active_models,
            metrics=metrics,
        )

        if not actions:
            logger.info("No actions required")
            return

        await self._execute_actions(actions)
