from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.telegram_bot import TelegramBot

class TelegramBotRepository:
    async def get_all_active(
        self,
        session: AsyncSession,
        
    ) -> list[TelegramBot]:
        result = await session.execute(select(TelegramBot).where(TelegramBot.is_active.is_(True)))
        return result.scalars().all()
    
    async def get_company_by_bot(
        self,
        session:AsyncSession,
        tg_bot_id: int,
        
    )-> int | None:
        result = await session.execute(select(TelegramBot.company_id).where(TelegramBot.tg_bot_id == tg_bot_id))
        return result.scalar_one_or_none()
    
    async def get_by_company(
        self,
        session: AsyncSession,
        company_id: int,
    ) -> TelegramBot | None:
        result = await session.execute(
            select(TelegramBot).where(
                TelegramBot.company_id == company_id,
                TelegramBot.is_active.is_(True),
            )
        )

        return result.scalar_one_or_none()