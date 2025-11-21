import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import os
from dotenv import load_dotenv
from handlers.admin import main_router
from handlers.news_queue import queue_router
import config
from database.base import get_db
from database.models.models import Post
from sqlalchemy import select
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def publish_scheduled_post():
    """Автоматически публикует посты из БД"""
    try:
        logger.info("🔍 Проверяем посты для публикации...")

        async for db_session in get_db():
            # Находим пост для публикации
            result = await db_session.execute(
                select(Post).where(Post.status == "parsed").order_by(Post.created_at).limit(1)
            )
            post = result.scalar()

            if post:
                logger.info(f"🎯 Публикуем пост: '{post.title}'")

                # Создаем временного бота для публикации
                bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

                # Формируем сообщение
                message_text = f"<b>{post.title}</b>\n\n{post.content or 'Нет текста'}"

                if post.source_url:
                    message_text += f"\n\n<a href='{post.source_url}'>📖 Читать полностью</a>"

                try:
                    # Публикуем в канал
                    sent_message = await bot.send_message(
                        chat_id=config.TARGET_CHANNEL_ID,
                        text=message_text,
                        disable_web_page_preview=False
                    )

                    logger.info(f"✅ Пост опубликован! ID: {sent_message.message_id}")

                    # Обновляем статус поста
                    post.status = "published"
                    post.telegram_message_id = sent_message.message_id
                    await db_session.commit()

                except Exception as e:
                    logger.error(f"❌ Ошибка публикации: {e}")

                finally:
                    await bot.session.close()
            else:
                logger.info("⏭️ Нет постов для публикации")

    except Exception as e:
        logger.error(f"❌ Ошибка в планировщике: {e}")


async def start_scheduler():
    """Запускает планировщик для автоматической публикации"""
    scheduler = AsyncIOScheduler()

    # Публикуем каждые 30 минут (можно изменить на config.PUBLISH_DELAY)
    scheduler.add_job(
        publish_scheduled_post,
        trigger=IntervalTrigger(minutes=30),
        id="publish_posts"
    )

    scheduler.start()
    logger.info("⏰ Планировщик публикации запущен (каждые 30 минут)")


async def main():
    token = os.getenv("BOT_TOKEN")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(main_router)
    dp.include_router(queue_router)

    # Запускаем планировщик публикации
    await start_scheduler()

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
        logger.info("Бот остановлен пользователем")