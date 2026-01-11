import asyncio

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import Message

from src.config import config
from src.dto import AppState
from src.services.user_model import UserModelService

router = Router()


@router.message(F.text & ~F.text.startswith("/"))
async def handle_user_message(message: Message, app_state: AppState) -> None:
    user_model = UserModelService(app_state.redis)
    consumer = app_state.kafka_consumer
    model = await user_model.get_selected_model(message.from_user.id)
    if not model:
        await message.answer("Сначала выбери модель через /start")
        return

    payload = {
        "user_id": message.from_user.id,
        "chat_id": message.chat.id,
        "message_id": message.message_id,
        "text": message.text,
        "model": model,
    }

    await app_state.kafka_producer.send_json(
        config.TOPIC_USER_MESSAGES,
        payload,
        key=str(message.from_user.id).encode("utf-8"),
    )
    req_user_id = message.from_user.id
    req_message_id = message.message_id

    try:
        async with asyncio.timeout(20):
            async for data in consumer:
                if data.get("user_id") != req_user_id:
                    continue
                if data.get("message_id") != req_message_id:
                    continue

                response = data.get("answer") or "Пустой ответ от модели"
                await message.answer(response, parse_mode=ParseMode.MARKDOWN)
                break
    except TimeoutError:
        await message.answer("Модель не ответила вовремя. Попробуйте позже.")
