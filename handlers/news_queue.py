from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy import select
from database.base import get_db
from database.models.models import Post
from .admin import is_admin
from keyboards.main_menu import get_queue_keyboard

queue_router = Router()


@queue_router.message(F.text == "📋 Очередь публикации")
@queue_router.message(Command("queue"))
async def show_queue(message: Message):
    if not is_admin(message.from_user.id):
        return

    async for db_session in get_db():
        result = await db_session.execute(
            select(Post).where(Post.status == "parsed").limit(10)
        )
        pending_posts = result.scalars().all()

        if not pending_posts:
            await message.answer("📭 Очередь публикации пуста")
            return

        text = "📋 Очередь публикации:\n\n"
        for i, post in enumerate(pending_posts, 1):
            text += f"{i}. {post.title}\n"
            text += f"   📝 {len(post.content)} символов\n\n"

        keyboard = get_queue_keyboard()
        await message.answer(text, reply_markup=keyboard)


@queue_router.callback_query(F.data == "publish_all")
async def publish_all(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    # TODO: Логика публикации всех постов
    await callback.answer("Все посты будут опубликованы!")


@queue_router.callback_query(F.data == "clear_queue")
async def clear_queue(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    # TODO: Логика очистки очереди
    await callback.answer("Очередь очищена!")