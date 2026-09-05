from repositories.instruction_repository import InstructionRepository
from repositories.telegram_bot_repository import TelegramBotRepository
from database.models.incubator import Instruction

from database.session import SessionLocal
class InstructionService:
    def __init__(self):
        self.instruction_repository = InstructionRepository()
        self.bot_repository = TelegramBotRepository()
        
    async def get_all_instructions(
        self,
        bot_id: int,
    )-> list[Instruction]:
        async with SessionLocal() as session:
            company_id = await self.bot_repository.get_company_by_bot(
                session = session, tg_bot_id =bot_id,
                
            )
            print(company_id)
            if company_id is None:
                return[]
            
            return await self.instruction_repository.get_all_instructions(session = session,company_id=company_id)
            
    async def get_script(
        self,
        id:int,
    )-> list:
        async with SessionLocal() as session:
            return await self.instruction_repository.get_script(session = session,id=id)    