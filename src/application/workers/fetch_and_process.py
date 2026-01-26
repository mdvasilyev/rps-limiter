from pathlib import Path

from src.application.services import LogsProcessor, RPSController


async def fetch_and_process():
    processor = LogsProcessor(Path("yaml-examples/entrypoint_metrics.txt"))

    await processor.load()
    processor.parse()

    rps = processor.calculate_rps()

    print(processor.count_requests())
    print("RPS:", rps)

    controller = RPSController(low=10, high=50)
    print(controller.evaluate(rps))
