from database.models.company import Company,Employee,EmployeeState
from database.models.telegram_bot import TelegramBot
from repositories.company_repository import CompanyRepository,EmployeeRepository,TelegramBotRepository
from database.session import SessionLocal


class CompanyService:

    def __init__(self):
        self.company_repository = CompanyRepository()
        self.employee_repository = EmployeeRepository()
        self.telegram_bot_repository = TelegramBotRepository()

    async def create_company(
        self,
        name: str,
        company_login: str,
        owner_password_hash: str,
        user_id:int,
        bot_token: str,
        tg_bot_id:int,
        
    ) -> Company:

        async with SessionLocal() as session:

            company = Company(
                name=name,
                company_login=company_login,
                owner_password_hash=owner_password_hash,
            )

            company = await self.company_repository.create(
                session=session,
                company=company,
            )
            print(company.id)
            
            
            employee = Employee(
                company_id=company.id,
                user_id=user_id,
                role=EmployeeState.OWNER,
            )    
            await self.employee_repository.create(
                session=session,
                employee=employee,
            )  
            
            telegram_bot = TelegramBot(
                company_id = company.id,
                token = bot_token,
                tg_bot_id = tg_bot_id,
                
            )
            
            await self.telegram_bot_repository.create(
                session = session,
                telegram_bot = telegram_bot
            ) 

            await session.commit()

            return company
    