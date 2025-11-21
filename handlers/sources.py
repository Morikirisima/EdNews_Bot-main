from aiogram import Router, F
from aiogram.types import Message
from keyboards.main_menu import main_kb
from keyboards.sources_kb import sources_kb

sources_router = Router()


@sources_router.message(F.text == "➕ Источники")
async def manage_sources(message: Message):
    # Временные данные источников
    sources_list = [
        {"id": 1, "name": "Минобрнауки", "type": "RSS", "status": "активен", "url": "https://минобрнауки.рф/rss"},
        {"id": 2, "name": "TJournal Образование", "type": "Парсинг", "status": "активен",
         "url": "https://tjournal.ru/education"},
        {"id": 3, "name": "RBC Образование", "type": "RSS", "status": "неактивен",
         "url": "https://www.rbc.ru/education"},
    ]

    text = "📡 *Управление источниками:*\n\n"

    for source in sources_list:
        status_icon = "✅" if source['status'] == "активен" else "❌"
        text += f"{status_icon} *{source['name']}*\n"
        text += f"   📝 Тип: {source['type']}\n"
        text += f"   🔗 URL: {source['url']}\n\n"

    text += "Выберите действие:"

    await message.answer(text, reply_markup=sources_kb, parse_mode="Markdown")


# 🔄 Включить/выключить источник
@sources_router.message(F.text == "🔄 Управление источниками")
async def toggle_sources(message: Message):
    text = """
🔄 *Включение/выключение источников:*

Нажмите на источник чтобы изменить его статус:

1. ✅ Минобрнауки (RSS)
2. ✅ TJournal Образование (Парсинг)  
3. ❌ RBC Образование (RSS)
"""
    await message.answer(text, parse_mode="Markdown")


# ➕ Добавить новый источник
@sources_router.message(F.text == "➕ Добавить источник")
async def add_source(message: Message):
    text = """
➕ *Добавление нового источника:*

Отправьте ссылку в одном из форматов:

• *RSS-лента:* 
  https://site.com/rss
  https://site.com/feed

• *Сайт для парсинга:*
  https://site.com/news
  https://site.com/education
"""
    await message.answer(text, parse_mode="Markdown")


# 📋 Тестирование источника
@sources_router.message(F.text == "🧪 Тестировать источник")
async def test_source(message: Message):
    await message.answer(
        "🧪 Тестирую подключение к источникам...\n"
        "Проверяю доступность и формат данных",
        reply_markup=sources_kb
    )


# ◀️ Назад в главное меню
@sources_router.message(F.text == "◀️ Главное меню")
async def back_to_main(message: Message):
    await message.answer(
        "Возвращаемся в главное меню:",
        reply_markup=main_kb
    )