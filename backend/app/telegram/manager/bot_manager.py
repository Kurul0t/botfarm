import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from telegram.main_bot.router import main_router
from telegram.client_bot.router import create_client_router


import core.app_state as app_state
load_dotenv()


async def loading():

    frames = ["|", "/", "-", "\\"]

    i = 0

    while True:

        print(f"\r {frames[i % 4]}    ", end="", flush=True)

        i += 1

        await asyncio.sleep(0.1)
    

class BotManager:

    def __init__(self):
        self.main_token = os.getenv("MAIN_BOT_TOKEN")

        if not self.main_token:
            raise ValueError("MAIN_BOT_TOKEN not found")

        self.main_bot = Bot(token=self.main_token)
        self.main_dp = Dispatcher()
        self.bots: dict[int, Bot] = {}

    def get_bot(self, bot_id: int) -> Bot | None:
            print("works")
            return self.bots.get(bot_id)
    
    async def start(self):
        self.main_dp.include_router(main_router)
        await app_state.reminder_manager.start()
        
        loading_task = asyncio.create_task(loading())
        print("Запуск головного бота")
        
        loading_task.cancel()
        print("\rГоловний бот запущен!")
        asyncio.create_task(
            self.main_dp.start_polling(
                self.main_bot
            )
        )
        print("Головний бот запущен!")
        
    async def create_bot(self, token: str):
        bot = Bot(token)
        # Отримуємо Telegram ID бота
        bot_info = await bot.get_me()
        bot_id = bot_info.id

        # Зберігаємо бота
        self.bots[bot_id] = bot

        dp = Dispatcher()

        router = create_client_router()
        dp.include_router(router)

        asyncio.create_task(
            dp.start_polling(bot)
        )

        print(f"Бот {token} запущений")
        
    