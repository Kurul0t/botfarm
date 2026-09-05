from aiogram import F, Router,Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from core import app_state
import ast
from services.reminder.reminder_service import pererobka
from datetime import datetime, timedelta
from aiogram.utils.keyboard import InlineKeyboardBuilder



from .states import StartIncubation


def create_incubation_router() -> Router:
    router = Router()

    

    @router.message(Command("start_incubation"))
    async def start_incubation(message:Message, state:FSMContext) -> None:
        await state.clear()
        
        await message.answer("⚙️Процедура запуску інкубатора⚙️\n\nЯку кількість яєць було закладено?\n(напишіть лише число)\n[1/3]")
        
        await state.set_state(StartIncubation.eggs_amount)
    
    
    @router.message(StartIncubation.eggs_amount, F.text)
    async def eggs_amount(message:Message, state:FSMContext,bot: Bot) -> None:
        eggs_amount = message.text.strip()
        if not eggs_amount.isdigit():
            await message.answer("Потрібно ввести ЛИШЕ ціле число")
            return
        
        await state.update_data(eggs_amount=eggs_amount)
        await state.set_state(StartIncubation.choose_incubator)
        
        incubators = await app_state.incubator_service.get_available_incubators(
                    bot_id=bot.id
                )
        builder = InlineKeyboardBuilder()
                
        for incubator in incubators:
            builder.button(
                text=f"Інкубатор №{incubator.number}",
                callback_data=f"incubator_id:{incubator.id}:{incubator.number}",
            )
        
        builder.adjust(1) 
        
        
        await message.answer("⚙️Процедура запуску інкубатора⚙️\n\nОберіть інкубатор\n[2/3]",reply_markup=builder.as_markup())



    @router.callback_query(StartIncubation.choose_incubator, F.data.startswith("incubator_id:"))
    async def choose_incubator(callback: CallbackQuery, state: FSMContext, bot: Bot,) -> None:
        incubator_id = int(callback.data.split(":")[1])
        incubator_number = int(callback.data.split(":")[2])
        await state.update_data(choose_incubator=incubator_id)
        await state.update_data(number = incubator_number)
        await state.set_state(StartIncubation.choose_instruction)
        print("choose_incubator")
        
        builder = InlineKeyboardBuilder()
                
        
        instructions = await app_state.instruction_service.get_all_instructions(
                    bot_id=bot.id
                )
        for instruction in instructions:
                    builder.button(
                        text=f"{instruction.title}",
                        callback_data=f"instruction_id:{instruction.id}:{instruction.title}",
                    )

        builder.adjust(1)
        await callback.message.answer(
            "⚙️Процедура запуску інкубатора⚙️\n\nОберіть інструкцію інкубування\n[3/3]"
,
            reply_markup=builder.as_markup(),
        )
            
            
    @router.callback_query(StartIncubation.choose_instruction,  F.data.startswith("instruction_id:"))
    async def choose_instruction(callback: CallbackQuery, state: FSMContext, bot: Bot,) -> None:
        instruction_id = int(callback.data.split(":")[1])
        instruction_title = str(callback.data.split(":")[2])
        

        data = await state.get_data()
        number_of_incubator = data.get("number")
        eggs_amount = data.get("eggs_amount")
        user_id = callback.from_user.id
        bot_id = bot.id
        script = await app_state.instruction_service.get_script(id = instruction_id)
        rem_list=[]
        if not script:
            print("База даних повернула порожній список.")
        script = script.strip('"')
        try:
            dictionary_format = "{" + script + "}"
            instruction_dict = ast.literal_eval(dictionary_format)
            print("Успішно конвертовано у словник:", instruction_dict)
        except Exception as e:
            print(f"Помилка конвертації рядка у словник: {e}")
            return
        for key, value in instruction_dict.items():
            rem_list.append((key, user_id, bot_id, value,number_of_incubator))
        print(rem_list)
        
        reminder_list = await pererobka(rem_list)
        for reminder in (reminder_list):
            await app_state.reminder_manager.add_reminder(reminder)
        await app_state.reminder_manager.restart()
        
        sheet = await app_state.google_sheet_service.write(bot_id)
        
        today_str = datetime.now().strftime("%d.%m.%Y")
        for index, worksheet in enumerate(sheet.worksheets()):
            if worksheet.title == "Інкубування":
                
                worksheet = sheet.get_worksheet(index)
                worksheet.append_row([number_of_incubator,"Етап 1",today_str, None,None,eggs_amount ])
        
        plus_17 = (datetime.now() + timedelta(days = 17)).strftime("%d.%m.%Y")
        
        await callback.message.answer(f"""✅ Інкубатор №{number_of_incubator} запущено успішно\n\nІнструкція "{instruction_title}"\nЯєць закладено: {eggs_amount}\nОрієнтовна дата вилупу: {plus_17}""")
        await app_state.incubator_service.update_state(bot_id=bot_id,number = number_of_incubator )
        await callback.answer()
        
    
    return router