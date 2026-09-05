from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete

from database.models.reminder import Reminder



class ReminderRepository:
    async def create(
        self,
        session:AsyncSession,
        reminder:Reminder,
    ) -> Reminder:
        session.add(reminder)
        await session.commit()
        await session.refresh(reminder)
         
        return reminder
    async def get_all(
        self,
        session:AsyncSession,
        
    ) -> list[Reminder]:
        result = await session.execute(
            select(Reminder)
        )
        return result.scalars().all()
    async def delete_(
        self,
        session:AsyncSession,
        list_:list,
    ):
        await session.execute(delete(Reminder).where(Reminder.id.in_(list_)))
        await session.commit()
    
    
