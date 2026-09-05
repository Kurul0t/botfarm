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
    @router.message(Command("t"))
    async def add_reminder(message: Message,bot:Bot):
        user_id = message.from_user.id
        bot_id = bot.id
        all_instruct = await app_state.instruction_service.get_all_instructions(bot_id=bot_id)
        print(all_instruct)
        rem_list=[]
        if not all_instruct:
            print("База даних повернула порожній список.")
        clean_str = all_instruct[0].strip('"')
        try:
            dictionary_format = "{" + clean_str + "}"
            instruction_dict = ast.literal_eval(dictionary_format)
            print("Успішно конвертовано у словник:", instruction_dict)
        except Exception as e:
            print(f"Помилка конвертації рядка у словник: {e}")
            return
        for key, value in instruction_dict.items():
            rem_list.append((key, user_id, bot_id, value))
        print(rem_list)
        
        reminder_list = await pererobka(rem_list)
        for reminder in (reminder_list):
            await app_state.reminder_manager.add_reminder(reminder)
        await app_state.reminder_manager.restart()

        await message.answer("✅ Нагадування створено через 1 хвилини.")
        
    
    
    
    
    
    return router