
import json
import logging
from urllib.parse import parse_qsl

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_session
from repositories.employee_repository import EmployeeRepository
from repositories.telegram_bot_repository import TelegramBotRepository
from services.client.telegram_auth import verify_telegram_init_data


router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)

employee_repository = EmployeeRepository()
bot_repository = TelegramBotRepository()


class TelegramAuthRequest(BaseModel):
    init_data: str


@router.post("/telegram")
async def telegram_auth(
    payload: TelegramAuthRequest,
    session: AsyncSession = Depends(get_session),
):
    # 1. Попередньо отримуємо Telegram ID
    try:
        raw_data = dict(
            parse_qsl(
                payload.init_data,
                keep_blank_values=True,
                strict_parsing=True,
            )
        )

        user = json.loads(raw_data["user"])
        telegram_user_id = user["id"]

        if type(telegram_user_id) is not int:
            raise ValueError("Invalid Telegram user ID")

    except (ValueError, KeyError, TypeError):
        logger.warning("AUTH FAILED: invalid Telegram data")

        raise HTTPException(
            status_code=401,
            detail="Некоректні Telegram-дані",
        )

    # 2. Шукаємо працівника за Telegram ID
    employee = await employee_repository.get_by_telegram_id(
        session=session,
        telegram_user_id=telegram_user_id,
    )

    if employee is None:
        logger.warning("AUTH FAILED: employee not found")

        raise HTTPException(
            status_code=403,
            detail="Користувача не знайдено",
        )

    # 3. Знаходимо бота компанії
    bot = await bot_repository.get_by_company(
        session=session,
        company_id=employee.company_id,
    )

    if bot is None:
        logger.warning("AUTH FAILED: company bot not found")

        raise HTTPException(
            status_code=403,
            detail="Бота компанії не знайдено",
        )

    # 4. Перевіряємо справжність Telegram initData
    verified_user = verify_telegram_init_data(
        init_data=payload.init_data,
        bot_token=bot.token,
    )

    # 5. Діагностика авторизації
    logger.warning("========== TELEGRAM AUTH DEBUG ==========")
    logger.warning("Employee ID: %s", employee.id)
    logger.warning("Employee Telegram ID: %s", employee.user_id)
    logger.warning("Company ID: %s", employee.company_id)
    logger.warning("Selected Bot ID: %s", bot.tg_bot_id)
    logger.warning(
        "Verification successful: %s",
        verified_user is not None,
    )
    logger.warning("=========================================")

    # 6. Перевіряємо результат валідації
    if verified_user is None:
        logger.warning(
            "AUTH FAILED: Telegram verification returned None"
        )

        raise HTTPException(
            status_code=401,
            detail="Не вдалося підтвердити Telegram-користувача",
        )

    # 7. Перевіряємо збіг Telegram ID
    if verified_user["id"] != employee.user_id:
        logger.warning("AUTH FAILED: Telegram user ID mismatch")

        raise HTTPException(
            status_code=401,
            detail="Не вдалося підтвердити Telegram-користувача",
        )

    # 8. Успішна авторизація
    logger.info(
        "AUTH SUCCESS: employee_id=%s, company_id=%s",
        employee.id,
        employee.company_id,
    )

    return {
        "employee_id": employee.id,
        "telegram_user_id": employee.user_id,
        "company_id": employee.company_id,
        "role": employee.role,
        "bot_id": bot.tg_bot_id,
    }
