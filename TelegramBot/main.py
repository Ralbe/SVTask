import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
import os
from config import API_TOKEN
from handlers import start, profile, ads, filters, creation

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

# Регистрация обработчиков
start.register_handlers(dp)
profile.register_handlers(dp)
ads.register_handlers(dp, bot)
filters.register_handlers(dp)
creation.register_handlers(dp)

async def main():
    try:
        await dp.start_polling(bot)
    finally:
        from DataBase.UserDB import close_connection
        close_connection()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())