from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.dto import AppState

router = Router()


@router.message(CommandStart())
async def start(
    message: Message,
    app_state: AppState,
):
    registry = app_state.model_registry
    models = await registry.list_models()

    if not models:
        await message.answer("Доступные модели отсутствуют. Попробуйте позже.")
        return

    keyboard = InlineKeyboardBuilder()
    for model in models:
        keyboard.button(
            text=model,
            callback_data=f"model:{model}",
        )

    await message.answer(
        "Выберите модель:",
        reply_markup=keyboard.as_markup(),
    )
