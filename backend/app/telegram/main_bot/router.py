from aiogram import Router,F
from aiogram.types import Message

from .handlers.registration.start import main_start_router
from .handlers.registration.create_company import main_create_company_router



main_router = Router()
main_router.include_router(main_start_router)
main_router.include_router(main_create_company_router)

"""@main_router.message(F.text)
async def echo(message: Message):
    await message.answer(message.text)
    
    await  app_state.bot_manager.create_bot(token="8252306876:AAFj9zVb9abqDNYsd3sJ0HCXD9SzbYgPFqw")"""