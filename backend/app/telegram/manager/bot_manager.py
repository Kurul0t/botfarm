
import asyncio
import os
import logging

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from telegram.main_bot.router import main_router
from telegram.client_bot.router import create_client_router
from services.client.mini_app import setup_mini_app

import core.app_state as app_state


load_dotenv()

logger = logging.getLogger(__name__)


class BotManager:

    def __init__(self):
        self.main_token = os.getenv("MAIN_BOT_TOKEN")

        if not self.main_token:
            raise ValueError("MAIN_BOT_TOKEN not found")

        self.main_bot = Bot(token=self.main_token)
        self.main_dp = Dispatcher()

        self.bots: dict[int, Bot] = {}
        self.tasks: dict[int, asyncio.Task] = {}

    def get_bot(self, bot_id: int) -> Bot | None:
        return self.bots.get(bot_id)

    async def start(self):
        self.main_dp.include_router(main_router)

        await app_state.reminder_manager.start()

        self.tasks[0] = asyncio.create_task(
            self.main_dp.start_polling(self.main_bot)
        )

        logger.info("Головний бот запущений")

    async def create_bot(self, token: str):
        bot = Bot(token=token)

        try:
            bot_info = await bot.get_me()
            bot_id = bot_info.id

            if bot_id in self.bots:
                logger.info(
                    "Бот %s вже запущений",
                    bot_id,
                )
                await bot.session.close()
                return

            # Автоматично налаштовуємо Mini App
            await setup_mini_app(bot)

            # Створюємо Dispatcher
            dp = Dispatcher()

            router = create_client_router()
            dp.include_router(router)

            # Запускаємо polling
            task = asyncio.create_task(
                dp.start_polling(bot)
            )

            # Зберігаємо бота
            self.bots[bot_id] = bot
            self.tasks[bot_id] = task

            logger.info(
                "Бот @%s (%s) запущений. Mini App налаштовано.",
                bot_info.username,
                bot_id,
            )

        except Exception:
            await bot.session.close()
            raise
