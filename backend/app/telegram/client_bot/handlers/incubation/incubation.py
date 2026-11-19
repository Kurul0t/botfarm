from aiogram import F, Router,Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from core import app_state
import json
from services.reminder.reminder_service import pererobka
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


from aiogram.utils.keyboard import InlineKeyboardBuilder


UA_TZ = ZoneInfo("Europe/Kyiv")

from .states import CheckIncubation, StartIncubation

import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def create_incubation_router() -> Router:
    router = Router()

    @router.message(Command("check_incubation"))
    async def  check_incubation(message: Message,bot:Bot,state:FSMContext)-> None:
        bot_id=bot.id
        company_id, incubators = await app_state.incubator_service.get_unavailable_incubators(bot_id=bot_id)
        text="⚙️Активні інкубатори⚙️\n\n"
        incubators_ = set()
        
        for incubator in incubators:

            count_days = (datetime.now(tz=UA_TZ) - incubator.activated_at).days
            
            text += f"Інкубатор №{incubator.number} [{incubator.eggs_amount}шт] -- {count_days} день\n"
            incubators_.add(incubator.number)

        await message.answer(text)
        await message.answer("Для детальної інформації про \nінкубацію, введіть НОМЕР інкубатора")
        
        await state.update_data(unavailable_incubators=incubators_)
        await state.update_data(company_id=company_id)
        await state.set_state(CheckIncubation.number)
        
    @router.message(CheckIncubation.number, F.text)
    async def check_incubation_number(message:Message, state: FSMContext)-> None:
        number = message.text.strip()
        data = await state.get_data()
        incubators = data.get("unavailable_incubators", set())
        company_id = data.get("company_id")
        
        if number.isdigit() and int(number) in incubators:
            
            instruction = await app_state.incubator_service.get_info_of_incubation(
                company_id=company_id,
                number=int(number)
            )
            await message.answer(instruction)
            await state.clear()
        else:
            await message.answer("❌ Номер інкубатора не коректний")         



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
            
            
    @router.callback_query(StartIncubation.choose_instruction, F.data.startswith("instruction_id:"))
    async def choose_instruction(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
        instruction_id = int(callback.data.split(":")[1])
        instruction_title = str(callback.data.split(":")[2])
        
        data = await state.get_data()
        number_of_incubator = data.get("number")
        eggs_amount = data.get("eggs_amount")
        user_id = callback.from_user.id
        bot_id = bot.id
        
        script = await app_state.instruction_service.get_script(
            id=instruction_id
        )

        if not script:
            await callback.message.answer(
                "❌ Інструкцію не знайдено."
            )
            return

        try:
            instruction = json.loads(script)

        except (json.JSONDecodeError, TypeError, AttributeError) as e:
            logger.error(f"Помилка обробки інструкції: {e}")
            await callback.message.answer(
                "❌ Помилка обробки інструкції."
            )
            return

        reminder_list = await pererobka(
            instruction=instruction,
            user_id=user_id,
            bot_id=bot_id,
            number=number_of_incubator,
        )
        for reminder in reminder_list:
            await app_state.reminder_manager.add_reminder(reminder)
        await app_state.reminder_manager.restart()
        
        # 2. Оновлюємо стан інкубатора в БД
        await app_state.incubator_service.update_incubators_info(
            bot_id=bot_id,
            number=number_of_incubator,
            incubators_info={
                "state": "incubating",
                "eggs_amount": int(eggs_amount),
                "instruction_id": int(instruction_id),
                "activated_at": datetime.now(tz=UA_TZ),
            },
        )
        
        # 3. МИТТЄВО НАДСИЛАЄМО ВІДПОВІДЬ КОРИСТУВАЧУ (щоб бот не зависать)
        plus_17 = (datetime.now() + timedelta(days=17)).strftime("%d.%m.%Y")
        await callback.message.answer(
            f"✅ Інкубатор №{number_of_incubator} запущено успішно\n\n"
            f"Інструкція: \"{instruction_title}\"\n"
            f"Яєць закладено: {eggs_amount}\n"
            f"Орієнтовна дата вилупу: {plus_17}"
        )
        await callback.answer() # Прибираємо годинничок на кнопці
        await state.clear()     # Скидаємо FSM стан
        
        # 4. БЕЗПЕЧНИЙ ЗАПИС В GOOGLE SHEETS (Якщо впаде тут — повідомлення користувач все одно отримає)
        
        sheet = await app_state.google_sheet_service.write(bot_id)
        today_str = datetime.now().strftime("%d.%m.%Y")
        print(f"АРКУШІ: {sheet.worksheets()}")
        
        for index, worksheet in enumerate(sheet.worksheets()):
            print(f"АРКУШ: {worksheet.title} ---- {index}")
            if worksheet.title == "Інкубування":
                target_worksheet = sheet.get_worksheet(index)
                
                # ЗАМІСТЬ None ПЕРЕДАЄМО ПОРОЖНІ РЯДКИ ""
                target_worksheet.append_row([
                    number_of_incubator, 
                    "Етап 1", 
                    today_str, 
                    "-->", 
                    plus_17, 
                    eggs_amount
                ])
                break # Зупиняємо цикл, бо лист уже знайдено
            else:
                logger.info(f"АРКУШУ НЕ ЗНАЙДЕНО")
        

        
    
    return router