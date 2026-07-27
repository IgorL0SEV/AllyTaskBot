"""
handlers/list_csv.py — команда /list_csv.

Генерирует CSV-файл со всеми задачами и отправляет его как документ.
CSV удобно открывать в Excel / LibreOffice / Google Sheets.
"""
from datetime import date

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message

from database.db import Database

router = Router(name="list_csv")


@router.message(Command("list_csv"))
async def cmd_list_csv(message: Message, db: Database) -> None:
    """Выгружает задачи в CSV и отправляет файлом."""
    buffer = db.export_csv()

    # Имя файла с датой, чтобы при повторных выгрузках файлы различались.
    filename = f"tasks_{date.today().isoformat()}.csv"

    # BufferedInputFile оборачивает байты в объект, который aiogram
    # отправит как документ (multipart/form-data).
    file = BufferedInputFile(file=buffer.read(), filename=filename)

    await message.answer_document(
        document=file,
        caption=f"📄 Выгрузка задач на {date.today().isoformat()}",
    )