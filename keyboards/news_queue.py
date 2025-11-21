from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Клавиатура для управления очередью
queue_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Опубликовать все"), KeyboardButton(text="❌ Очистить очередь")],
        [KeyboardButton(text="👁️ Просмотреть детали"), KeyboardButton(text="◀️ Главное меню")]
    ],
    resize_keyboard=True
)

# Инлайн клавиатура для конкретных действий с новостью
def get_news_actions_kb(news_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Опубликовать", callback_data=f"publish_{news_id}"),
                InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete_{news_id}")
            ],
            [
                InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_{news_id}"),
                InlineKeyboardButton(text="👁️ Просмотреть", callback_data=f"view_{news_id}")
            ]
        ]
    )