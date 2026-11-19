from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.company import Employee


class EmployeeRepository:

    async def get_by_telegram_id(
        self,
        session: AsyncSession,
        telegram_user_id: int,
    ) -> Employee | None:

        result = await session.execute(
            select(Employee).where(
                Employee.user_id == telegram_user_id
            )
        )

        return result.scalar_one_or_none()