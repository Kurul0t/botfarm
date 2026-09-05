from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models.company import Company,Employee,GoogleSheet
from database.models.telegram_bot import TelegramBot


class CompanyRepository:

    async def create(
        self,
        session: AsyncSession,
        company: Company,
    ) -> Company:

        session.add(company)

        await session.flush()

        await session.refresh(company)

        return company
    
class EmployeeRepository:

    async def create(
        self,
        session: AsyncSession,
        employee: Employee,
    ) -> Employee:

        session.add(employee)

        await session.flush()

        return employee
    
class TelegramBotRepository:
    async def create(
        self,
        session:AsyncSession,
        telegram_bot:TelegramBot,
    ) -> TelegramBot:
        session.add(telegram_bot)
        await session.flush()
        return telegram_bot
    
    
class GoogleSheetRepository:
    async def get_key(
        self,
        session:AsyncSession,
        company_id:int,
        
    )-> str | None:
        result = await session.execute(select(GoogleSheet.key).where(GoogleSheet.company_id==company_id))
        return result.scalar_one_or_none()