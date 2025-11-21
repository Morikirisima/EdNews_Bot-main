from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Главная клавиатура админа
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Очередь публикации"), KeyboardButton(text="📝 На модерации")],
        [KeyboardButton(text="🔄 Запустить парсинг"), KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="⚙️ Настройки")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие..."
)

# Клавиатура для управления очередью
def get_queue_keyboard(post_id=None):
    if post_id:
        # Клавиатура для конкретного поста
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Опубликовать", callback_data=f"publish_{post_id}"),
                    InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete_{post_id}")
                ],
                [
                    InlineKeyboardButton(text="👀 Предпросмотр", callback_data=f"preview_{post_id}"),
                    InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_{post_id}")
                ]
            ]
        )
    else:
        # Общая клавиатура для очереди
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="📤 Опубликовать все", callback_data="publish_all"),
                    InlineKeyboardButton(text="🗑️ Очистить очередь", callback_data="clear_queue")
                ]
            ]
        )

# Клавиатура для постов на модерации
def get_moderation_keyboard(post_id=None):
    if post_id:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{post_id}"),
                    InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{post_id}")
                ],
                [
                    InlineKeyboardButton(text="✂️ Сократить", callback_data=f"shorten_{post_id}"),
                    InlineKeyboardButton(text="👀 Предпросмотр", callback_data=f"preview_{post_id}")
                ]
            ]
        )
    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Одобрить все", callback_data="approve_all"),
                    InlineKeyboardButton(text="🗑️ Очистить", callback_data="clear_moderation")
                ]
            ]
        )