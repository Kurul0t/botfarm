from aiogram import Router

from .handlers.incubation.incubation import create_incubation_router
from .handlers.instruction.instruction import create_instruction_router
from .handlers.menu import client_menu_router


def create_client_router() -> Router:
    router = Router()

    router.include_router(create_incubation_router())
    router.include_router(create_instruction_router())
    router.include_router(client_menu_router)

    return router