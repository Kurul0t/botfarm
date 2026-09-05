from sqlalchemy import select,and_,update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.incubator import Incubator,IncubatorState

class IncubatorRepository:
    async def get_all_available(
        self,
        session = AsyncSession,
        company_id=int,
    ) -> list[Incubator]:
        result = await session.execute(select(Incubator).where(and_(Incubator.company_id == company_id, Incubator.state == IncubatorState.AVAILABLE,)))
        return result.scalars().all()
    async def change_state(
        self,
        session:AsyncSession,
        company_id:int,
        number:int,
    ):
        await session.execute(update(Incubator).where(Incubator.company_id == company_id,Incubator.number == number).values(state=IncubatorState.INCUBATING.value))
        
        await session.commit()