from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models.command import Command

class CommandRepository:
    async def read_command(
        self,
        session: AsyncSession,
        command_id:int, 
    ):
        result = await session.execute(select(Command.function_name, Command.arguments).where(Command.id == command_id))
        return result.fetchone()