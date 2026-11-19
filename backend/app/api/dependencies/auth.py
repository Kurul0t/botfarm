import json
from urllib.parse import parse_qsl

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_session
from repositories.employee_repository import EmployeeRepository
from repositories.telegram_bot_repository import TelegramBotRepository
from services.client.telegram_auth import verify_telegram_init_data


employee_repository = EmployeeRepository()
bot_repository = TelegramBotRepository()


async def get_current_employee(
    init_data: str = Header(alias="X-Telegram-Init-Data"),
    session: AsyncSession = Depends(get_session),
):
    # 1. Отримуємо Telegram ID користувача
    try:
        data = dict(parse_qsl(init_data))
        user = json.loads(data["user"])
        telegram_user_id = user["id"]

        if type(telegram_user_id) is not int:
            raise ValueError()

    except (ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Некоректні Telegram-дані",
        )

    # 2. Знаходимо працівника в БД
    employee = await employee_repository.get_by_telegram_id(
        session=session,
        telegram_user_id=telegram_user_id,
    )

    if employee is None:
        raise HTTPException(
            status_code=403,
            detail="Працівника не знайдено",
        )

    # 3. Знаходимо бота компанії
    bot = await bot_repository.get_by_company(
        session=session,
        company_id=employee.company_id,
    )

    if bot is None:
        raise HTTPException(
            status_code=403,
            detail="Бота компанії не знайдено",
        )

    # 4. Перевіряємо підпис Telegram
    verified_user = verify_telegram_init_data(
        init_data=init_data,
        bot_token=bot.token,
    )

    if verified_user is None:
        raise HTTPException(
            status_code=401,
            detail="Недійсний підпис Telegram",
        )

    if verified_user["id"] != employee.user_id:
        raise HTTPException(
            status_code=401,
            detail="Telegram ID не збігається",
        )

    # 5. Повертаємо авторизованого працівника
    return employee