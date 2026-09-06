import asyncio
from datetime import datetime, timedelta

from aiogram import Router,Bot
from aiogram.types import Message
from aiogram.filters import Command


from html import escape

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from .states import CompanyRegistrationStates as CompanyRegistration

from services.reminder.reminder_service import pererobka
from ...keyboards.keyboards import confirmation_keyboard
import core.app_state as app_state


main_create_company_router = Router()


  
@main_create_company_router.message(Command("register"))
async def start_registration(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()

    await message.answer(
        "Розпочинаємо реєстрацію підприємства.\n\n"
        "Введіть назву підприємства:"
    )
    

    await state.set_state(CompanyRegistration.company_name)
    
@main_create_company_router.message(CompanyRegistration.company_name, F.text)
async def receive_company_name(
    message: Message,
    state: FSMContext,
) -> None:
    company_name = message.text.strip()

    if len(company_name) < 2:
        await message.answer(
            "Назва занадто коротка. Введіть щонайменше 2 символи:"
        )
        return

    await state.update_data(company_name=company_name)
    await state.set_state(CompanyRegistration.bot_token)

    await message.answer(
        "Надішліть токен Telegram-бота, отриманий від BotFather:"
    )
    
@main_create_company_router.message(CompanyRegistration.bot_token, F.text)
async def receive_bot_token(
    message: Message,
    state: FSMContext,
) -> None:
    bot_token = message.text.strip()

    if ":" not in bot_token:
        await message.answer(
            "Токен має неправильний формат. Спробуйте ще раз:"
        )
        return

    await state.update_data(bot_token=bot_token)
    await state.set_state(CompanyRegistration.admin_login)

    await message.answer(
        "Придумайте адміністративний ЛОГІН для керування ботом:"
    )


@main_create_company_router.message(CompanyRegistration.admin_login, F.text)
async def receive_admin_login(
    message: Message,
    state: FSMContext,
) -> None:
    admin_login = message.text.strip()

    if len(admin_login) < 4:
        await message.answer(
            "Логін має містити щонайменше 4 символи. Спробуйте ще раз:"
        )
        return

    await state.update_data(admin_login=admin_login)
    await state.set_state(CompanyRegistration.admin_password)

    await message.answer(
        "Придумайте адміністративний ПАРОЛЬ"
    )

@main_create_company_router.message(
    CompanyRegistration.admin_password,
    F.text,
)
async def receive_admin_password(
    message: Message,
    state: FSMContext,
) -> None:
    admin_password = message.text.strip()

    if len(admin_password) < 8:
        await message.answer(
            "Пароль має містити щонайменше 8 символів. Спробуйте ще раз:"
        )
        return

    await state.update_data(admin_password=admin_password)

    data = await state.get_data()

    await state.set_state(CompanyRegistration.confirmation)

    await message.answer(
        "<b>Перевірте заявку:</b>\n\n"
        f"<b>Підприємство:</b> {escape(data['company_name'])}\n"
        f"<b>Логін:</b> {escape(data['admin_login'])}\n"
        "<b>Пароль:</b> ••••••••\n\n"
        "Токен отримано та буде перевірено перед створенням заявки.",
        reply_markup=confirmation_keyboard,
        parse_mode="HTML",
    )

    # Видаляємо повідомлення з паролем із чату, якщо Telegram дозволить.
    try:
        await message.delete()
    except Exception:
        pass
    
    
@main_create_company_router.callback_query(
    CompanyRegistration.confirmation,
    F.data == "company_registration_confirm",
)
async def confirm_registration(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    data = await state.get_data()


    user_id=callback.from_user.id
    bot_token=data["bot_token"]
    bot = Bot(token=bot_token)

    me = await bot.get_me()

    print("Заявка на реєстрацію:", data)
    try:
        company = await app_state.company_service.create_company(
            name=data["company_name"],
            company_login=data["admin_login"],
            owner_password_hash=data["admin_password"],
            user_id=user_id,
            bot_token=bot_token,
            tg_bot_id=me.id,
            
        )

        await state.clear()
        await app_state.bot_manager.create_bot(bot_token)

        if callback.message:
            await callback.message.edit_text(
                "✅ Заявку на реєстрацію надіслано адміністратору. Очікуйте підтвердження та подальшої інструкції"
            )

        await callback.answer()
    except Exception as e:
        print("Помилка при створенні компанії:", e)
        if callback.message:
            await callback.message.edit_text(
                "❌ Сталася помилка при створенні компанії. Будь ласка, спробуйте ще раз пізніше.Або зверніфться до адміністратора."
            )
        await callback.answer()
    


@main_create_company_router.callback_query(
    CompanyRegistration.confirmation,
    F.data == "company_registration_cancel",
)
async def cancel_registration(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.clear()

    if callback.message:
        await callback.message.edit_text(
            "Реєстрацію підприємства скасовано."
        )

    await callback.answer()