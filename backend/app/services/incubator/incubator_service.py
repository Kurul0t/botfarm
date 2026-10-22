
from repositories.instruction_repository import InstructionRepository
from repositories.telegram_bot_repository import TelegramBotRepository
from repositories.incubator_repository import IncubatorRepository

from database.models.incubator import Incubator
from database.session import SessionLocal


class IncubatorService:

    def __init__(self):
        self.bot_repository = TelegramBotRepository()
        self.incubator_repository = IncubatorRepository()
        self.instruction_repository = InstructionRepository()

    async def get_available_incubators(
        self,
        bot_id: int,
    ) -> list[Incubator]:

        async with SessionLocal() as session:

            company_id  = await self.bot_repository.get_company_by_bot(
                session=session,
                tg_bot_id=bot_id,
            )

            if company_id  is None:
                return []

            return await self.incubator_repository.get_all_available(
                session=session,
                company_id=company_id 
            )
    async def get_unavailable_incubators(
        self,
        bot_id: int,
    ) -> list[Incubator]:
        async with SessionLocal() as session:
            company_id  = await self.bot_repository.get_company_by_bot(
                session=session,
                tg_bot_id=bot_id,
            )
            
            if company_id  is None:
                return []
            
            all_unavailable =  await self.incubator_repository.get_all_unavailable(
                session = session,
                company_id = company_id
            )
            return company_id,all_unavailable
    async def get_info_of_incubation(
        self,
        company_id: int,
        number:int,
        
    ):
        async with SessionLocal() as session:
            instruction_id = await self.incubator_repository.get_instruction_id(
                session = session,
                company_id = company_id,
                number = number
            )
            
            return await self.instruction_repository.get_instruction_by_id(
                session = session,
                id = instruction_id,
            )
        
        
    async def update_state(
        self,
        bot_id:int,
        number:int,
        val:str
    ):
        async with SessionLocal() as session:
            company_id  = await self.bot_repository.get_company_by_bot(
                session=session,
                tg_bot_id=bot_id,
            )

            if company_id  is None:
                return []

            await self.incubator_repository.change_state(
                session=session,
                company_id=company_id, 
                number = number,
                value_ = val,
            )