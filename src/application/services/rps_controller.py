class RPSController:
    def __init__(self, low: float, high: float):
        self.low = low
        self.high = high

    def evaluate(self, rps: float) -> str:
        if rps < self.low:
            return "scale_down"
        if rps > self.high:
            return "scale_up"
        return "stable"
