from aiogram import Router
from aiogram.types import CallbackQuery
from redis.asyncio import Redis

from src.config import config

router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith("model:"))
async def model_select(
    call: CallbackQuery,
    redis: Redis,
):
    model = call.data.split("model:", 1)[1].strip()

    if not model:
        await call.answer("Некорректная модель", show_alert=False)
        return

    key = config.USER_MODEL_KEY_PATTERN.format(
        user_id=call.from_user.id,
    )

    await redis.set(
        key,
        model,
        ex=60 * 60 * 24 * 30,
    )

    await call.answer(
        f"Выбрана модель: {model}",
        show_alert=False,
    )
    await call.message.answer(
        f"Текущая модель: {model}",
    )
