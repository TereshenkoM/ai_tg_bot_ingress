from aiogram import F, Router
from aiogram.types import Message

from src.config import config
from src.dto import AppState
from src.services.user_model import UserModelService

router = Router()


@router.message(F.text & ~F.text.startswith("/"))
async def handle_user_message(message: Message, app_state: AppState) -> None:
    user_model = UserModelService(app_state.redis)

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

    await app_state.kafka.send_json(
        config.TOPIC_USER_MESSAGES,
        payload,
        key=str(message.from_user.id).encode("utf-8"),
    )

    await message.answer("Сообщение спродюсировано")
