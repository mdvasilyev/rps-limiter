from datetime import UTC, datetime
from math import ceil

from src.domain.dto.booking import UnbookAction
from src.domain.dto.model import ModelDTO, ModelRpsIncreaseDTO, ScaleAction
from src.domain.dto.notificator import WarnUnbookingAction
from src.domain.dto.rps_data import (
    DeleteIdleModelQuery,
    GetIdleModelQuery,
    PostIdleModelQuery,
)
from src.domain.interfaces.repositories import IRpsDataRepository
from src.domain.interfaces.services import IDecisionMaker


class DecisionMaker(IDecisionMaker):
    def __init__(
        self,
        rps_data_repository: IRpsDataRepository,
        rps_threshold: float,
        warn_after_mins: int,
        unbook_after_mins: int,
    ) -> None:
        self._rps_data_repository = rps_data_repository
        self._rps_threshold = rps_threshold
        self._warn_after_mins = warn_after_mins
        self._unbook_after_mins = unbook_after_mins

    async def process(
        self,
        increase_interval: int,
        active_models: list[ModelDTO],
        metrics: list[ModelRpsIncreaseDTO],
    ) -> list[ScaleAction | UnbookAction | WarnUnbookingAction]:
        actions: list[ScaleAction | UnbookAction | WarnUnbookingAction] = []

        metrics_map = {m.model_name: m for m in metrics}

        for model in active_models:
            user_id = model.instance.owner_id
            model_name = model.name

            metric = metrics_map.get(model_name)

            rps = metric.rps if metric else 0.0
            increase = metric.requests if metric else 0.0

            replicas = model.instance.replicas
            target_replicas = ceil(rps / self._rps_threshold)

            idle_model = await self._rps_data_repository.get_idle_model(
                query=GetIdleModelQuery(user_id=user_id, model_name=model_name)
            )

            if increase == 0 or target_replicas == 0:
                if idle_model:
                    time_diff = datetime.now(UTC) - idle_model.timestamp
                    if time_diff.total_seconds() >= self._unbook_after_mins * 60:
                        actions.append(
                            UnbookAction(
                                user_id=user_id,
                                model_name=model_name,
                            )
                        )
                    elif time_diff.total_seconds() >= self._warn_after_mins * 60:
                        actions.append(
                            WarnUnbookingAction(
                                user_id=user_id,
                                model_name=model_name,
                            )
                        )
                else:
                    await self._rps_data_repository.post_idle_model(
                        query=PostIdleModelQuery(user_id=user_id, model_name=model_name)
                    )
            elif replicas != target_replicas:
                if idle_model:
                    await self._rps_data_repository.delete_idle_model(
                        query=DeleteIdleModelQuery(
                            user_id=user_id, model_name=model_name
                        )
                    )

                actions.append(ScaleAction(model_id=model.id, replicas=target_replicas))

        return actions
