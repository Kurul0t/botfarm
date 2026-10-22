from aiogram.fsm.state import State, StatesGroup

class StartIncubation(StatesGroup):
    eggs_amount = State()
    choose_instruction = State()
    choose_incubator = State()
    number = State()
    confirmation = State()
    
class CheckIncubation(StatesGroup):
    number = State()
    unavailable_incubators = State()
    company_id = State()
    eggs_amount = State()
