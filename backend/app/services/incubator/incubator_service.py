
from repositories.instruction_repository import InstructionRepository
from repositories.telegram_bot_repository import TelegramBotRepository
from repositories.incubator_repository import IncubatorRepository

from database.models.incubator import Incubator
from database.session import SessionLocal
import json

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from database.models.incubator import IncubatorState

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
    
    async def update_parameters(
        self,
        bot_id: int,
        number: int,
        parameters: dict,
    ):
        async with SessionLocal() as session:
            company_id = await self.bot_repository.get_company_by_bot(
                session=session,
                tg_bot_id=bot_id,
            )

            if company_id is None:
                raise ValueError("Компанію не знайдено")

            await self.incubator_repository.change_parameters(
                session=session,
                company_id=company_id,
                number=number,
                parameters=parameters,
            )
            
    async def get_parameters(
        self,
        bot_id: int,
        number: int,
    ):
        async with SessionLocal() as session:
            company_id = await self.bot_repository.get_company_by_bot(
                session=session,
                tg_bot_id=bot_id
            )

            if company_id is None:
                return {}

            return await self.incubator_repository.get_parameters(
                session=session,
                company_id=company_id,
                number=number
            )
            
    async def get_parameters_by_id(
        self,
        company_id: int,
        incubator_id: int,
    ) -> dict | None:

        async with SessionLocal() as session:
            return await self.incubator_repository.get_parameters_by_id(
                session=session,
                company_id=company_id,
                incubator_id=incubator_id
            )
            
    async def get_incubation_progress(
        self,
        company_id: int,
        incubator_id: int,
    ) -> dict | None:

        async with SessionLocal() as session:
            incubator = await self.incubator_repository.get_by_id(
                session=session,
                company_id=company_id,
                incubator_id=incubator_id,
            )

            if incubator is None:
                return None

            result = {
                "duration_days": None,
                "current_day": None,
                "days_remaining": None,
                "estimated_end_at": None,
                "progress": None,
            }

            if (
                incubator.state != IncubatorState.INCUBATING.value
                or incubator.activated_at is None
                or incubator.instruction_id is None
            ):
                return result

            instruction = await self.instruction_repository.get_instruction_by_id(
                session=session,
                id=incubator.instruction_id,
            )

            if instruction is None:
                return result

            script = instruction.script
            data = json.loads(script) if isinstance(script, str) else script

            duration_days = data.get("duration_days")

            if (
                not isinstance(duration_days, int)
                or isinstance(duration_days, bool)
                or duration_days <= 0
            ):
                return result

            ua_tz = ZoneInfo("Europe/Kyiv")

            start = incubator.activated_at

            # Припускаємо, що datetime без timezone зберігався
            # за місцевим часом України.
            if start.tzinfo is None:
                start = start.replace(tzinfo=ua_tz)

            start = start.astimezone(timezone.utc)
            now = datetime.now(timezone.utc)

            end = start + timedelta(days=duration_days)

            elapsed_seconds = max(
                0,
                (now - start).total_seconds(),
            )

            total_seconds = duration_days * 86400

            progress = min(
                100.0,
                elapsed_seconds / total_seconds * 100,
            )

            current_day = min(
                duration_days,
                max(1, int(elapsed_seconds // 86400) + 1),
            )

            remaining_seconds = max(
                0,
                (end - now).total_seconds(),
            )

            days_remaining = (
                int(-(-remaining_seconds // 86400))
                if remaining_seconds > 0
                else 0
            )

            return {
                "duration_days": duration_days,
                "current_day": current_day,
                "days_remaining": days_remaining,
                "estimated_end_at": end.astimezone(ua_tz),
                "progress": round(progress, 2),
            }
            
            
    async def update_incubators_info(
        self,
        bot_id: int,
        number: int,
        incubators_info: dict,
    ):
        async with SessionLocal() as session:
            company_id = await self.bot_repository.get_company_by_bot(
                session=session,
                tg_bot_id=bot_id,
            )

            if company_id is None:
                raise ValueError("Компанію не знайдено")

            await self.incubator_repository.change_incubators_info(
                session=session,
                company_id=company_id,
                number=number,
                info=incubators_info,
            )
    