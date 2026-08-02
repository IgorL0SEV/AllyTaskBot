"""
handlers/list.py — команда /list.

Выводит все задачи из базы данных единым сообщением. Тексты (пустой
список — Меню 10, заголовок и строка задачи — Меню 11) в menus.py.
"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.db import Database
from menus import MENU_10_EMPTY, MENU_11_HEADER, MENU_11_ROW

router = Router(name="list")


def _format_tasks(tasks: list) -> str:
    """Превращает строки из БД в красивый текст для Telegram.

    Каждая строка: (id, text, user, created_at, status, category)
    """
    if not tasks:
        return MENU_10_EMPTY

    lines = [MENU_11_HEADER]
    for task_id, text, user, created_at, status, category in tasks:
        lines.append(
            MENU_11_ROW.format(
                task_id=task_id,
                text=text,
                user=user,
                category=category,
                status=status,
                created_at=created_at,
            )
        )
    return "\n\n".join(lines)


@router.message(Command("list"))
async def cmd_list(message: Message, db: Database) -> None:
    """Достаёт все задачи из БД и отправляет списком."""
    tasks = db.get_all_tasks()
    await message.answer(_format_tasks(tasks))