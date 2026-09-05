from aiogram.fsm.state import State, StatesGroup


class CompanyRegistrationStates(StatesGroup):
    
    company_name = State()
    bot_token = State()
    admin_login = State()
    admin_password = State()
    confirmation = State()
