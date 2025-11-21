from aiogram import Router, F
from aiogram.types import Message
from keyboards.main_menu import main_kb
from keyboards.news_queue import queue_kb

queue_router = Router()


@queue_router.message(F.text == "📰 Очередь новостей")
async def show_news_queue(message: Message):
    # Временные данные для примера (потом заменишь на реальные из БД)
    news_queue = [
        {"id": 1, "title": "Новые стандарты образования в 2024", "source": "Минобр", "status": "ожидает"},
        {"id": 2, "title": "IT-классы в школах Москвы", "source": "TJournal", "status": "ожидает"},
        {"id": 3, "title": "Гранты для студентов", "source": "RBC", "status": "ожидает"}
    ]

    if not news_queue:
        await message.answer(
            "📭 Очередь новостей пуста\n\n"
            "Запустите парсинг или добавьте новые источники",
            reply_markup=main_kb
        )
        return

    # Формируем текст с очередью
    text = "📰 *Очередь новостей:*\n\n"
    for news in news_queue:
        text += f"📍 *{news['title']}*\n"
        text += f"   📚 Источник: {news['source']}\n"
        text += f"   ⏳ Статус: {news['status']}\n\n"

    text += "Выберите действие:"

    await message.answer(text, reply_markup=queue_kb, parse_mode="Markdown")

@queue_router.message(F.text == "✅ Опубликовать все")
async def publish_all_news(message: Message):
    await message.answer(
        "🔄 Публикую все новости из очереди...\n"
        "Это может занять несколько минут",
        reply_markup=main_kb
    )
    # Здесь будет логика публикации

@queue_router.message(F.text == "❌ Очистить очередь")
async def clear_queue(message: Message):
    await message.answer(
        "🗑️ Очередь новостей очищена",
        reply_markup=main_kb
    )
    # Здесь будет логика очистки

@queue_router.message(F.text == "👁️ Просмотреть детали")
async def show_news_details(message: Message):
    # Показываем детали первой новости в очереди
    news_details = """
📋 *Детали новости:*

*Заголовок:* Новые стандарты образования в 2024
*Источник:* Минобрнауки
*Дата:* 15.01.2024
*Категория:* 🎓 Профобразование

*Краткое содержание:*
В 2024 году вступают в силу новые образовательные стандарты, которые затрагивают...
"""
    await message.answer(news_details, parse_mode="Markdown")

@queue_router.message(F.text == "◀️ Главное меню")
async def back_to_main(message: Message):
    await message.answer(
        "Возвращаемся в главное меню:",
        reply_markup=main_kb
    )