from datetime import timedelta
from math import ceil

from src.domain.dto.booking import UnbookAction
from src.domain.dto.model import ModelDTO, ModelRpsIncreaseDTO, ScaleAction
from src.domain.interfaces.services import IDecisionMaker


class DecisionMaker(IDecisionMaker):
    def __init__(
        self,
        rps_threshold: float,
        warn_after_mins: int,
        unbook_after_mins: int,
    ) -> None:
        self._rps_threshold = rps_threshold
        self._warn_after_mins = timedelta(minutes=warn_after_mins)
        self._unbook_after_mins = timedelta(minutes=unbook_after_mins)

    def process(
        self,
        active_models: list[ModelDTO],
        metrics: list[ModelRpsIncreaseDTO],
    ) -> list[ScaleAction | UnbookAction]:
        actions: list[ScaleAction | UnbookAction] = []

        metrics_map = {m.model_name: m for m in metrics}

        for model in active_models:
            model_name = model.name
            model_id = model.id

            metric = metrics_map.get(model_name)

            rps = metric.rps if metric else 0.0
            increase = metric.requests if metric else 0.0

            replicas = model.instance.replicas
            target_replicas = ceil(rps / self._rps_threshold)

            if increase == 0 or target_replicas == 0:
                actions.append(
                    UnbookAction(model_name=model_name, user_id=model.instance.owner_id)
                )
            elif replicas != target_replicas:
                actions.append(ScaleAction(model_id=model_id, replicas=target_replicas))

        return actions
