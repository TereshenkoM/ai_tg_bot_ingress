from aiogram import Router

from src.handlers import message, model_select, start


def setup_routers() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(model_select.router)
    router.include_router(message.router)
    return router
