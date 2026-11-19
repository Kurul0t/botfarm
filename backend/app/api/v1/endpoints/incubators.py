
import json
from io import BytesIO

import qrcode
from PIL import Image, ImageDraw, ImageFont

from aiogram import Bot
from aiogram.types import BufferedInputFile
from aiogram.exceptions import (
    TelegramAPIError,
    TelegramForbiddenError,
)
from core import app_state
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_employee
from database.session import get_session
from database.models.company import Employee

from repositories.incubator_repository import (
    IncubatorRepository,
)
from repositories.telegram_bot_repository import (
    TelegramBotRepository,
)

from schemas.incubator import IncubatorResponse


router = APIRouter(
    prefix="/incubators",
    tags=["Incubators"],
)

repository = IncubatorRepository()
bot_repository = TelegramBotRepository()


# ==========================================
# ОТРИМАННЯ ВСІХ ІНКУБАТОРІВ
# ==========================================

@router.get("/", response_model=list[IncubatorResponse])
async def get_incubators(
    employee: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session),
):
    incubators = await repository.get_all(
        session=session,
        company_id=employee.company_id,
    )

    return incubators


# ==========================================
# ОТРИМАННЯ ОДНОГО ІНКУБАТОРА
# ==========================================

@router.get(
    "/{incubator_id}",
    response_model=IncubatorResponse,
)
async def get_incubator(
    incubator_id: int,
    employee: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session),
):
    incubator = await repository.get_by_id(
        session=session,
        company_id=employee.company_id,
        incubator_id=incubator_id,
    )

    if incubator is None:
        raise HTTPException(
            status_code=404,
            detail="Інкубатор не знайдено",
        )

    parameters = await repository.get_parameters_by_id(
        session=session,
        company_id=employee.company_id,
        incubator_id=incubator_id,
    )

    incubation = await app_state.incubator_service.get_incubation_progress(
        company_id=employee.company_id,
        incubator_id=incubator_id,
    )
    instruction_title = None

    if incubator.instruction_id is not None:
        instruction = await app_state.incubator_service.instruction_repository.get_instruction_by_id(
            session=session,
            id=incubator.instruction_id,
        )

        if instruction is not None:
            instruction_title = instruction.title

    return {
        **IncubatorResponse.model_validate(incubator).model_dump(),
        "instruction_title": instruction_title,
        "parameters": parameters or {},
        **(incubation or {}),
    }


# ==========================================
# ГЕНЕРАЦІЯ PNG-ЕТИКЕТКИ
# ==========================================


def generate_qr_png(incubator) -> bytes:
    qr_data = json.dumps(
        {
            "v": 1,
            "type": "incubator",
            "id": incubator.device_code,
            "action": "details",
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )

    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=4,
    )

    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_image = qr.make_image(
        fill_color="black",
        back_color="white",
    ).convert("RGB")

    # 35 × 45 мм при 300 DPI
    width = 413
    height = 531

    image = Image.new(
        "RGB",
        (width, height),
        "white",
    )

    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(
            "DejaVuSans.ttf", 22
        )
    except OSError:
        font = ImageFont.load_default()

    draw.text(
        (width // 2, 35),
        "SMART FARM",
        fill="black",
        font=font,
        anchor="mm",
    )

    draw.text(
        (width // 2, 75),
        f"Інкубатор #{incubator.number}",
        fill="black",
        font=font,
        anchor="mm",
    )

    # QR-код
    qr_image = qr_image.resize(
        (345, 345),
        Image.Resampling.NEAREST,
    )

    image.paste(
        qr_image,
        ((width - 345) // 2, 100),
    )

    draw.text(
        (width // 2, 480),
        incubator.device_code,
        fill="black",
        font=font,
        anchor="mm",
    )

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG",
        dpi=(300, 300),
    )

    return buffer.getvalue()



# ==========================================
# НАДСИЛАННЯ QR У TELEGRAM
# ==========================================

@router.post("/{incubator_id}/send-qr")
async def send_incubator_qr(
    incubator_id: int,
    employee: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session),
):
    # 1. Отримуємо інкубатор компанії
    incubator = await repository.get_by_id(
        session=session,
        company_id=employee.company_id,
        incubator_id=incubator_id,
    )

    if incubator is None:
        raise HTTPException(
            status_code=404,
            detail="Інкубатор не знайдено",
        )

    if not incubator.device_code:
        raise HTTPException(
            status_code=400,
            detail="В інкубатора відсутній device_code",
        )

    # 2. Отримуємо Telegram-бота компанії
    telegram_bot = await bot_repository.get_by_company(
        session=session,
        company_id=employee.company_id,
    )

    if telegram_bot is None:
        raise HTTPException(
            status_code=404,
            detail="Бота компанії не знайдено",
        )

    # 3. Генеруємо PNG
    try:
        png_bytes = generate_qr_png(incubator)

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Помилка генерації QR-коду",
        )

    # 4. Готуємо Telegram-документ
    filename = (
        f"incubator-{incubator.device_code}.png"
    )

    document = BufferedInputFile(
        file=png_bytes,
        filename=filename,
    )

    # 5. Надсилаємо файл користувачу
    try:
        async with Bot(
            token=telegram_bot.token
        ) as bot:

            await bot.send_document(
                chat_id=employee.user_id,
                document=document,
                caption=(
                    f"QR-код інкубатора №{incubator.number}\n"
                    f"Код: {incubator.device_code}"
                ),
            )

    except TelegramForbiddenError:
        raise HTTPException(
            status_code=403,
            detail=(
                "Бот не може надіслати файл. "
                "Відкрийте чат із ботом "
                "та натисніть /start."
            ),
        )

    except TelegramAPIError:
        raise HTTPException(
            status_code=502,
            detail=(
                "Не вдалося надіслати "
                "PNG через Telegram"
            ),
        )

    # 6. Успішна відповідь
    return {
        "success": True,
        "message": "QR-код надіслано в Telegram",
        "filename": filename,
    }



# ==========================================
# ПОТОЧНІ ПАРАМЕТРИ ІНКУБАЦІЇ
# ==========================================

@router.get("/{incubator_id}/parameters")
async def get_incubator_parameters(
    incubator_id: int,
    employee: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session),
):
    parameters = await repository.get_parameters_by_id(
        session=session,
        company_id=employee.company_id,
        incubator_id=incubator_id,
    )

    if parameters is None:
        raise HTTPException(
            status_code=404,
            detail="Інкубатор не знайдено",
        )

    return {
        "parameters": parameters,
    }