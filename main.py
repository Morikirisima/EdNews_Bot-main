import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import os
from dotenv import load_dotenv
from handlers.admin import main_router
from handlers.news_queue import queue_router
from handlers.sources import sources_router

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    token = os.getenv("BOT_TOKEN")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(main_router)
    dp.include_router(queue_router)
    dp.include_router(sources_router)

    try:
        logger.info("Бот запущен...")

        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Ошибка при запуске бота {e}")

    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info("Бот оставлен пользователем")


