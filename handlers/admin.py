from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards import main_kb
import config

main_router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in config.ADMINS_IDS

@main_router.message(CommandStart())
async def start(message: Message):
    if not await is_admin(message.from_user.id):
        await message.answer("❌ Этот бот доступен только администраторам канала")
        return

    await message.answer(
        "👋 Панель управления EdNews Channel",
        reply_markup=main_kb
    )