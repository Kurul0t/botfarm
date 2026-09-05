from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command,CommandStart


main_start_router = Router()

@main_start_router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Вітаю! Це головний бот. \nВикористовуйте команду \n/menu для доступу до меню.")
    
@main_start_router.message(Command("menu"))
async def menu_handler(message: Message):
    await message.answer("Меню головного бота: \n1. Опція 1\n2. Опція 2\n3. Опція 3")