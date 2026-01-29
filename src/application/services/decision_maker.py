from datetime import datetime, timedelta

from dataclasses import dataclass


@dataclass
class ModelState:
    last_rps: float | None
    zero_since: datetime | None


@dataclass(frozen=True)
class ScaleUp:
    model: str


@dataclass(frozen=True)
class ScaleDown:
    model: str


@dataclass(frozen=True)
class WarnUnbooking:
    model: str


@dataclass(frozen=True)
class Unbook:
    model: str


class LogsProcessor:
    SCALE_UP_THRESHOLD = 20.0
    SCALE_DOWN_THRESHOLD = 5.0

    WARN_AFTER = timedelta(minutes=10)
    UNBOOK_AFTER = timedelta(minutes=20)

    def __init__(self):
        self._state: dict[str, ModelState] = {}

    def process(
        self,
        *,
        active_models: list[str],
        rps_by_model: dict[str, float],
        increase_by_model: dict[str, float],
    ) -> list:
        now = datetime.utcnow()
        actions = []

        for model in active_models:
            rps = rps_by_model.get(model, 0.0)
            increase = increase_by_model.get(model, 0.0)

            state = self._state.setdefault(
                model,
                ModelState(last_rps=None, zero_since=None),
            )

            # SCALE LOGIC
            if state.last_rps is not None:
                if rps > state.last_rps and rps >= self.SCALE_UP_THRESHOLD:
                    actions.append(ScaleUp(model))

                elif rps < state.last_rps and rps <= self.SCALE_DOWN_THRESHOLD:
                    actions.append(ScaleDown(model))

            # INACTIVITY LOGIC
            if increase == 0:
                state.zero_since = state.zero_since or now
                inactive_for = now - state.zero_since

                if inactive_for >= self.UNBOOK_AFTER:
                    actions.append(Unbook(model))
                elif inactive_for >= self.WARN_AFTER:
                    actions.append(WarnUnbooking(model))
            else:
                state.zero_since = None

            state.last_rps = rps

        return actions
