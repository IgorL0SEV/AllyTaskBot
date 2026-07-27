"""
handlers/keyboards.py — inline-клавиатуры для бота.

Inline-клавиатуры — это кнопки, прикреплённые к сообщению.
При нажатии Telegram присылает боту callback с данными кнопки
(мы их кладём в callback_data), а бот реагирует в обработчике.

Справочники значений хранятся здесь же, чтобы и кнопки, и обработчики
использовали один источник истины.
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Справочник категорий: callback_data -> отображаемый текст
CATEGORIES = {
    "front": "Фронт-энд",
    "back": "Бэк-энд",
    "db": "База данных",
    "common": "Общее",
}

# Справочник статусов
STATUSES = {
    "new": "Новое",
    "in_progress": "В работе",
    "done": "Выполнено",
}


def categories_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора категории при добавлении задачи."""
    builder = InlineKeyboardBuilder()
    for callback_data, label in CATEGORIES.items():
        # callback_data = "category:<value>" — обработчик в add.py парсит это
        builder.button(text=label, callback_data=f"category:{callback_data}")
    # По 2 кнопки в ряд — компактно смотрится в Telegram
    builder.adjust(2)
    return builder.as_markup()


def statuses_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора статуса при добавлении задачи."""
    builder = InlineKeyboardBuilder()
    for callback_data, label in STATUSES.items():
        builder.button(text=label, callback_data=f"status:{callback_data}")
    builder.adjust(2)
    return builder.as_markup()


def get_category_label(callback_data: str) -> str:
    """Возвращает человекочитаемое название категории по ключу."""
    return CATEGORIES.get(callback_data, callback_data)


def get_status_label(callback_data: str) -> str:
    """Возвращает человекочитаемое название статуса по ключу."""
    return STATUSES.get(callback_data, callback_data)