from datetime import datetime, timedelta

from src.domain.dto import ModelInfo, ModelState, Scale, Unbook, WarnUnbooking
from src.domain.interfaces import IDecisionMaker


class DecisionMaker(IDecisionMaker):
    SCALE_UP_THRESHOLD = 20.0
    SCALE_DOWN_THRESHOLD = 5.0

    WARN_AFTER = timedelta(minutes=10)
    UNBOOK_AFTER = timedelta(minutes=20)

    def __init__(self) -> None:
        self._state: dict[str, ModelState] = {}

    def process(
        self,
        active_models: list[ModelInfo],
        rps_by_model: dict[str, float],
        increase_by_model: dict[str, float],
    ) -> list[Scale | WarnUnbooking | Unbook]:
        now = datetime.utcnow()
        actions: list[Scale | WarnUnbooking | Unbook] = []

        for model in active_models:
            model_name = model.name
            model_id = model.id
            rps: float = rps_by_model.get(model_name, 0.0)
            increase: float = increase_by_model.get(model_name, 0.0)

            state: ModelState = self._state.setdefault(
                model_name,
                ModelState(last_rps=None, zero_since=None),
            )

            if state.last_rps is not None:
                replicas = model.instance.replicas
                # TODO проверить соотношение количества реплик к RPS
                if rps > state.last_rps and rps >= self.SCALE_UP_THRESHOLD:
                    actions.append(Scale(model_id, replicas + 1))

                elif rps < state.last_rps and rps <= self.SCALE_DOWN_THRESHOLD:
                    actions.append(Scale(model_id, replicas - 1))

            if increase == 0:
                state.zero_since = state.zero_since or now
                inactive_for = now - state.zero_since

                user_id = model.instance.ownerId
                if inactive_for >= self.UNBOOK_AFTER:
                    actions.append(Unbook(model_id, model_name, user_id))
                elif inactive_for >= self.WARN_AFTER:
                    actions.append(WarnUnbooking(model_id, user_id))
            else:
                state.zero_since = None

            state.last_rps = rps

        return actions
