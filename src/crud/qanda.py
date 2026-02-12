from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.baserepository import BaseRepository
from src.models.qanda import QandA
from src.schemas.qanda import QandACreate, QandAUpdate


class QandARepository(BaseRepository[QandA]):
    """
    QandA-specific repository – inherits common CRUD from BaseRepository
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, QandA)

    async def create(self, qanda_data: QandACreate) -> QandA:
        return await super().create(qanda_data.model_dump())

    async def get_by_id(self, qanda_id: int) -> QandA | None:
        return await super().get_by_id(qanda_id)

    async def update(
        self, qanda_id: int, update_data: QandAUpdate
    ) -> QandA | None:
        values = update_data.model_dump(exclude_unset=True)
        return await super().update(qanda_id, values)

    async def delete(self, qanda_id: int) -> QandA | None:
        return await super().delete(qanda_id)