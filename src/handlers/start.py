from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.services.model_registry import ModelRegistry

router = Router()


@router.message(CommandStart())
async def start(
    message: Message,
    model_registry: ModelRegistry,
):
    models = await model_registry.list_models()

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
