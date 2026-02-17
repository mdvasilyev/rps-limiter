from datetime import UTC, datetime, timedelta

from src.domain.dto import ModelDTO, ModelState, Scale, Unbook, WarnUnbooking
from src.domain.interfaces import IDecisionMaker


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
        self._state: dict[str, ModelState] = {}

    def process(
        self,
        active_models: list[ModelDTO],
        rps_by_model: dict[str, float],
        increase_by_model: dict[str, float],
    ) -> list[Scale | WarnUnbooking | Unbook]:
        now = datetime.now(UTC)
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

                if rps > state.last_rps and rps >= self._scale_up_threshold:
                    actions.append(Scale(model_id, replicas + 1))

                elif rps < state.last_rps and rps <= self._scale_down_threshold:
                    actions.append(Scale(model_id, replicas - 1))

            if increase == 0:
                state.zero_since = state.zero_since or now
                inactive_for = now - state.zero_since

                user_id = model.instance.owner_id
                if inactive_for >= self._unbook_after_mins:
                    actions.append(Unbook(model_id, model_name, user_id))
                elif inactive_for >= self._warn_after_mins:
                    actions.append(WarnUnbooking(model_id, user_id))
            else:
                state.zero_since = None

            state.last_rps = rps

        return actions
