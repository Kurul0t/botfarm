from aiogram import F, Router,Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from aiogram.utils.keyboard import InlineKeyboardBuilder



from core import app_state
from services.reminder.reminder_service import pererobka

import ast




def create_instruction_router() -> Router:
    router = Router()
    
    
        
    
    return router