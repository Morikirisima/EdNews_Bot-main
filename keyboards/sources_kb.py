from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

sources_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить источник"), KeyboardButton(text="🔄 Управление источниками")],
        [KeyboardButton(text="🧪 Тестировать источник"), KeyboardButton(text="📋 Список источников")],
        [KeyboardButton(text="◀️ Главное меню")]
    ],
    resize_keyboard=True
)