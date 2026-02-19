from datetime import timedelta
from math import ceil

from src.domain.dto import ModelDTO, ModelRpsIncreaseDTO, Scale, Unbook
from src.domain.interfaces.services import IDecisionMaker


class DecisionMaker(IDecisionMaker):
    def __init__(
        self,
        scale_up_threshold: float,
        scale_down_threshold: float,
        warn_after_mins: int,
        unbook_after_mins: int,
    ) -> None:
        self._scale_up_threshold = scale_up_threshold
        self._scale_down_threshold = scale_down_threshold
        self._warn_after_mins = timedelta(minutes=warn_after_mins)
        self._unbook_after_mins = timedelta(minutes=unbook_after_mins)

    def process(
        self,
        active_models: list[ModelDTO],
        metrics: list[ModelRpsIncreaseDTO],
    ) -> list[Scale | Unbook]:
        actions: list[Scale | Unbook] = []

        metrics_map = {m.model_name: m for m in metrics}

        for model in active_models:
            model_name = model.name
            model_id = model.id

            metric = metrics_map.get(model_name)

            rps = metric.rps if metric else 0.0
            increase = metric.requests if metric else 0.0

            replicas = model.instance.replicas
            target_replicas = ceil(rps / self._scale_up_threshold)

            if increase == 0:
                actions.append(
                    Unbook(model_name=model_name, user_id=model.instance.owner_id)
                )
            elif replicas != target_replicas:
                actions.append(Scale(model_id=model_id, replicas=target_replicas))

        return actions
