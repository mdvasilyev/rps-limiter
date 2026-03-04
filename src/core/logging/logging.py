import os
import socket
import sys

from loguru import logger

from src.core.configurations.config.config import LoggingConfig


def setup_logging(config: LoggingConfig) -> None:
    logger.remove()

    instance_id = (
        os.getenv("POD_NAME")
        or os.getenv("HOSTNAME")
        or socket.gethostname()
        or "unknown"
    )

    extra = {
        "service": config.service_name,
        "instance": instance_id,
        "pod_name": os.getenv("POD_NAME"),
        "pod_namespace": os.getenv("POD_NAMESPACE"),
        "node_name": os.getenv("NODE_NAME"),
    }

    logger.configure(extra=extra)
    logger.add(
        sys.stdout,
        level=config.level.upper(),
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
            "{extra[service]} | {extra[instance]} | "
            "{name}:{function}:{line} - {message}"
        ),
        serialize=config.json,
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )
