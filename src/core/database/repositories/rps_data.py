from sqlalchemy import delete, select

from src.core.database.manager import PostgresConnectionManager
from src.core.database.models import IdleModel
from src.domain.dto.rps_data import (
    DeleteIdleModelQuery,
    GetIdleModelQuery,
    IdleModelDTO,
    PostIdleModelQuery,
)
from src.domain.interfaces.repositories import IRpsDataRepository


class RpsDataRepository(IRpsDataRepository):
    def __init__(self, connection_manager: PostgresConnectionManager) -> None:
        self._connection_manager = connection_manager

    async def get_idle_model(self, query: GetIdleModelQuery) -> IdleModelDTO | None:
        async with self._connection_manager.get_session() as session:
            stmt = (
                select(IdleModel)
                .where(
                    IdleModel.user_id == query.user_id,
                    IdleModel.model_name == query.model_name,
                )
                .order_by(IdleModel.timestamp.desc())
            )
            row = (await session.execute(stmt)).scalars().first()
            if row is None:
                return None
            return IdleModelDTO(
                id=row.id,
                user_id=row.user_id,
                model_name=row.model_name,
                timestamp=row.timestamp,
            )

    async def post_idle_model(self, query: PostIdleModelQuery) -> IdleModelDTO:
        async with self._connection_manager.get_session() as session:
            model = IdleModel(
                user_id=query.user_id,
                model_name=query.model_name,
                timestamp=query.timestamp,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return IdleModelDTO(
                id=model.id,
                user_id=model.user_id,
                model_name=model.model_name,
                timestamp=model.timestamp,
            )

    async def delete_idle_model(self, query: DeleteIdleModelQuery) -> dict[str, str]:
        async with self._connection_manager.get_session() as session:
            stmt = delete(IdleModel).where(
                IdleModel.user_id == query.user_id,
                IdleModel.model_name == query.model_name,
            )
            result = await session.execute(stmt)
            await session.commit()
            if result.rowcount and result.rowcount > 0:
                return {"status": "ok", "message": "idle models deleted"}
            return {"status": "ok", "message": "idle models not found"}
