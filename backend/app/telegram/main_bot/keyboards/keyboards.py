from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


confirmation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Підтвердити",
                callback_data="company_registration_confirm",
            ),
            InlineKeyboardButton(
                text="❌ Скасувати",
                callback_data="company_registration_cancel",
            ),
        ]
    ]
)