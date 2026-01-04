from aiogram import Router

from src.handlers import model_select, start


def setup_router() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(model_select.router)
    return router
