from aiogram import Router

from .handlers.incubation.incubation import create_incubation_router
from .handlers.instruction.instruction import create_instruction_router


def create_client_router() -> Router:
    router = Router()

    router.include_router(create_incubation_router())
    router.include_router(create_instruction_router())


    return router