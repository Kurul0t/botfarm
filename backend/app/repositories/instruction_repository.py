from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models.incubator import Instruction


class InstructionRepository:
    async def get_all_instructions(
        self,
        session = AsyncSession,
        company_id = int,
    ) -> list[Instruction]:
        result= await session.execute(select(Instruction).where(Instruction.company_id == company_id))
        instructions = list(result.scalars().all())
        return instructions
        
    async def get_script(
        self,
        session:AsyncSession,
        id:int,
    ):
        result = await session.execute(select(Instruction.script).where(Instruction.id == id))
        
        return result.scalar_one_or_none()