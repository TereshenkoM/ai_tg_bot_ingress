import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from src.config import config


dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет")


async def main():
    bot = Bot(token=config.TG_BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())