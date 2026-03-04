from faststream.asgi import AsgiResponse, get
from faststream.asgi.types import ASGIApp, Scope
from faststream.rabbit import RabbitBroker
from loguru import logger
from sqlalchemy import select

from src.core.database.manager import PostgresConnectionManager


@get(include_in_schema=False)
async def liveness(_: Scope) -> AsgiResponse:
    return AsgiResponse(b"", status_code=204)


def readiness(
    broker: RabbitBroker,
    connection_manager: PostgresConnectionManager,
) -> ASGIApp:
    ok = AsgiResponse(b"", status_code=204)
    fail = AsgiResponse(b"", status_code=500)

    @get(include_in_schema=False)
    async def _ready(_: Scope) -> AsgiResponse:
        try:
            await broker.ping(timeout=5.0)
        except Exception:
            logger.exception("RabbitMQ not ready")
            return fail

        try:
            async with connection_manager.get_session() as session:
                await session.execute(select(1))
        except Exception:
            logger.exception("Postgres not ready")
            return fail

        return ok

    return _ready
