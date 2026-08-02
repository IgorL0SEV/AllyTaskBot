"""
handlers/keyboards.py — сборка inline-клавиатур бота.

Inline-клавиатура — это кнопки, прикреплённые к сообщению. При нажатии
Telegram присылает боту callback с данными кнопки (мы кладём их в
callback_data), а бот реагирует в обработчике.

Тексты кнопок (категории, статусы) живут в menus.py (Меню 1 и Меню 2).
Здесь только логика сборки клавиатур и lookup подписей по ключу.
Чтобы добавить/переименовать/удалить кнопку — правьте menus.py.
"""
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from menus import MENU_1_CATEGORIES, MENU_2_STATUSES


def categories_keyboard() -> InlineKeyboardMarkup:
    """Собирает inline-клавиатуру категорий из menus.MENU_1_CATEGORIES."""
    builder = InlineKeyboardBuilder()
    for key, label in MENU_1_CATEGORIES.items():
        # callback_data = "category:<key>" — обработчик в add.py парсит это
        builder.button(text=label, callback_data=f"category:{key}")
    builder.adjust(2)  # по 2 кнопки в ряд
    return builder.as_markup()


def statuses_keyboard() -> InlineKeyboardMarkup:
    """Собирает inline-клавиатуру статусов из menus.MENU_2_STATUSES."""
    builder = InlineKeyboardBuilder()
    for key, label in MENU_2_STATUSES.items():
        builder.button(text=label, callback_data=f"status:{key}")
    builder.adjust(2)
    return builder.as_markup()


def get_category_label(key: str) -> str:
    """Возвращает подпись категории по внутреннему ключу (из Меню 1)."""
    return MENU_1_CATEGORIES.get(key, key)


def get_status_label(key: str) -> str:
    """Возвращает подпись статуса по внутреннему ключу (из Меню 2)."""
    return MENU_2_STATUSES.get(key, key)