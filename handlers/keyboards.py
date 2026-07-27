"""
handlers/keyboards.py — inline-клавиатуры для бота.

Inline-клавиатуры — это кнопки, прикреплённые к сообщению.
При нажатии Telegram присылает боту callback с данными кнопки
(мы их кладём в callback_data), а бот реагирует в обработчике.

================================================================
  КАК ИЗМЕНИТЬ КНОПКИ (меню категорий и статусов)
================================================================
Вся настройка — в двух словарях ниже: CATEGORIES и STATUSES.

    "ключ":  "Текст на кнопке"
     ↑           ↑
  внутренний   видит пользователь
   ключ        в Telegram
  (латиницей,
   не меняйте
   у старых
   кнопок)

ДОБАВИТЬ кнопку — впишите новую строку по аналогии:
    "design": "Дизайн",

УДАЛИТЬ кнопку — сотрите строку.
ПЕРЕИМЕНОВАТЬ подпись — поменяйте текст справа (ключ оставьте).

Порядок строк = порядок кнопок в Telegram.
В БД сохраняется текст справа (например, «Фронт-энд»), поэтому
у старых задач подпись останется прежней — это нормально.
================================================================
"""
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ------------------------------------------------------------------
# МЕНЮ: КАТЕГОРИИ
# ------------------------------------------------------------------
CATEGORIES = {
    "front":  "Фронт-энд",
    "back":   "Бэк-энд",
    "db":     "База данных",
    "common": "Общее",
}

# ------------------------------------------------------------------
# МЕНЮ: СТАТУСЫ
# ------------------------------------------------------------------
STATUSES = {
    "new":         "Новое",
    "in_progress": "В работе",
    "done":        "Выполнено",
}


# ------------------------------------------------------------------
# Сборка клавиатур (дальше можно не читать — код строит кнопки сам)
# ------------------------------------------------------------------
def categories_keyboard() -> InlineKeyboardMarkup:
    """Собирает inline-клавиатуру из словаря CATEGORIES."""
    builder = InlineKeyboardBuilder()
    for key, label in CATEGORIES.items():
        # callback_data = "category:<key>" — обработчик в add.py парсит это
        builder.button(text=label, callback_data=f"category:{key}")
    builder.adjust(2)  # по 2 кнопки в ряд
    return builder.as_markup()


def statuses_keyboard() -> InlineKeyboardMarkup:
    """Собирает inline-клавиатуру из словаря STATUSES."""
    builder = InlineKeyboardBuilder()
    for key, label in STATUSES.items():
        builder.button(text=label, callback_data=f"status:{key}")
    builder.adjust(2)
    return builder.as_markup()


def get_category_label(key: str) -> str:
    """Возвращает подпись категории по внутреннему ключу."""
    return CATEGORIES.get(key, key)


def get_status_label(key: str) -> str:
    """Возвращает подпись статуса по внутреннему ключу."""
    return STATUSES.get(key, key)