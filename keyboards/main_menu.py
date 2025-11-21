from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Обычная клавиатура
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📰 Очередь новостей"), KeyboardButton(text="➕ Источники")],
        [KeyboardButton(text="🏷️ Фильтры"), KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="🔄 Запустить парсинг")]
    ],
    resize_keyboard=True
)

# Инлайн клавиатура для новостей ✅ ДОБАВЬ ЭТУ ПЕРЕМЕННУЮ
news_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🎓 Образование", callback_data="news_edu"),
         InlineKeyboardButton(text="💻 IT в школе", callback_data="news_it")],
        [InlineKeyboardButton(text="🏛️ Господдержка", callback_data="news_gov"),
         InlineKeyboardButton(text="📊 Статистика", callback_data="news_stats")],
        [InlineKeyboardButton(text="🔔 Подписаться", callback_data="subscribe")]
    ]
)