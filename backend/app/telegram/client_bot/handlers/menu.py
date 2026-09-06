from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command


client_menu_router = Router()


@client_menu_router.message(Command("menu"))
async def menu_handler(message: Message):
    await message.answer("Меню клієнтського бота: \n/start_incubation")