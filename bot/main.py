
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings")  # <- твой путь к settings
django.setup()
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs
from bot.bot import bot
from bot.dialogs import dialog_router  
from bot.api import api
from bot.config import BOT_TOKEN



async def main():

    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(dialog_router)

    setup_dialogs(dp)

    await api.login()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())