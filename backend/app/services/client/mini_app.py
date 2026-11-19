import os

from aiogram import Bot
from aiogram.types import MenuButtonWebApp, WebAppInfo
from dotenv import load_dotenv

load_dotenv()


async def setup_mini_app(bot: Bot) -> None:
    mini_app_url = os.getenv("MINI_APP_URL")

    if not mini_app_url:
        raise ValueError("MINI_APP_URL not found in .env")

    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="Smart Farm",
            web_app=WebAppInfo(url=mini_app_url),
        ),
    )