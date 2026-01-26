import asyncio
from pathlib import Path
from typing import Dict, List, Tuple

from prometheus_client.parser import text_string_to_metric_families


class LogsProcessor:
    def __init__(self, metrics_path: Path):
        self.metrics_path = metrics_path
        self.raw_text: str | None = None
        self.samples: List[Tuple[str, dict, float]] = []

    async def load(self) -> None:
        if not self.metrics_path.exists():
            raise FileNotFoundError(f"Metrics file not found: {self.metrics_path}")

        loop = asyncio.get_running_loop()
        self.raw_text = await loop.run_in_executor(None, self.metrics_path.read_text)

    def parse(self) -> None:
        if self.raw_text is None:
            raise RuntimeError("Metrics text not loaded")

        self.samples.clear()

        for family in text_string_to_metric_families(self.raw_text):
            for sample in family.samples:
                name, labels, value = sample[:3]
                self.samples.append((name, labels, float(value)))

    def count_requests(self) -> Dict[str, object]:
        total = 0
        per_handler: Dict[str, int] = {}

        for name, labels, value in self.samples:
            if name != "http_requests_total":
                continue

            v = int(value)
            total += v

            handler = labels.get("handler", "unknown")
            per_handler[handler] = per_handler.get(handler, 0) + v

        return {
            "total_requests": total,
            "per_handler": per_handler,
        }

    def calculate_rps(self) -> float:
        total_requests = 0.0
        cpu_seconds = None

        for name, _, value in self.samples:
            if name == "http_requests_total":
                total_requests += value

            elif name == "process_cpu_seconds_total":
                cpu_seconds = value

        if cpu_seconds is None:
            raise RuntimeError("process_cpu_seconds_total not found")

        if cpu_seconds <= 0:
            return 0.0

        return total_requests / cpu_seconds
