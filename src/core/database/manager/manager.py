from asyncio import Lock
from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.configurations.config import PostgresConfig


class PostgresConnectionManager:
    """Connection manager for PostgreSQL database"""

    def __init__(
        self,
        config: PostgresConfig,
    ) -> None:
        """Initialize connection manager entity."""
        self._config = config
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._lock = Lock()

    @property
    def initialized(self) -> bool:
        return self._engine is not None and self._session_factory is not None

    async def refresh(self) -> None:
        """(Re-)create connection engine."""
        await self.shutdown()

        self._engine = create_async_engine(
            f"postgresql+asyncpg://{self._config.user}:{self._config.password}@{self._config.host}"
            f":{self._config.port}/{self._config.db}",
            future=True,
            max_overflow=5,
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )
        try:
            async with self._engine.connect() as conn:
                cur = await conn.execute(select(1))
                assert cur.fetchone()[0] == 1
        except Exception as exc:
            self._engine = None
            self._session_factory = None
            raise RuntimeError(
                "something wrong with database connection, aborting"
            ) from exc

    async def shutdown(self) -> None:
        """Dispose connection pool and deinitialize."""
        if self.initialized:
            async with self._lock:
                if self.initialized:
                    await self._engine.dispose()
                self._engine = None
                self._session_factory = None

    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        """Get an async SQLAlchemy session."""
        if not self.initialized:
            async with self._lock:
                if not self.initialized:
                    await self.refresh()
        async with self._session_factory() as session:
            yield session
