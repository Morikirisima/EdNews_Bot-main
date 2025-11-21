from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# Главное меню админа
admin_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📰 Источники новостей", callback_data="admin_sources"),
         InlineKeyboardButton(text="🏷️ Управление тегами", callback_data="admin_tags")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
         InlineKeyboardButton(text="⏰ Расписание", callback_data="admin_schedule")],
        [InlineKeyboardButton(text="🔄 Парсинг сейчас", callback_data="parse_now"),
         InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin_settings")]
    ]
)

# Управление источниками
sources_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить источник", callback_data="add_source")],
        [InlineKeyboardButton(text="📋 Список источников", callback_data="list_sources")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back")]
    ]
)

# Управление тегами/категориями
tags_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🎓 Профобразование", callback_data="toggle_prof"),
         InlineKeyboardButton(text="💻 IT в школах", callback_data="toggle_it")],
        [InlineKeyboardButton(text="🏛️ Господдержка", callback_data="toggle_gov"),
         InlineKeyboardButton(text="🌍 Международное", callback_data="toggle_int")],
        [InlineKeyboardButton(text="✅ Применить теги", callback_data="apply_tags"),
         InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back")]
    ]
)

# Статистика
stats_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📈 За сегодня", callback_data="stats_today"),
         InlineKeyboardButton(text="📅 За неделю", callback_data="stats_week")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="stats_users"),
         InlineKeyboardButton(text="📰 Новости", callback_data="stats_news")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back")]
    ]
)