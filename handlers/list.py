"""
handlers/list.py — команда /list.

Выводит все задачи из базы данных единым сообщением.
"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.db import Database

router = Router(name="list")


def _format_tasks(tasks: list) -> str:
    """Превращает строки из БД в красивый текст для Telegram.

    Каждая строка: (id, text, user, created_at, status, category)
    """
    if not tasks:
        return "📭 Задач пока нет. Добавьте первую командой <b>/add</b>."

    lines = ["<b>📋 Все задачи:</b>\n"]
    for task_id, text, user, created_at, status, category in tasks:
        lines.append(
            f"<b>#{task_id}</b> — {text}\n"
            f"   👤 {user} · 📁 {category} · 🚦 {status} · 🕒 {created_at}"
        )
    return "\n\n".join(lines)


@router.message(Command("list"))
async def cmd_list(message: Message, db: Database) -> None:
    """Достаёт все задачи из БД и отправляет списком."""
    tasks = db.get_all_tasks()
    await message.answer(_format_tasks(tasks))