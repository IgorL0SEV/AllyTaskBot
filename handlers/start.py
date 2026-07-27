"""
handlers/start.py — обработчик команды /start.

/start — приветствие пользователя и краткая справка по командам.
"""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="start")


# Приветственный текст. HTML-разметка включена в main.py (ParseMode.HTML),
# поэтому можно использовать <b>жирный</b>, <i>курсив</i>, и т.д.
WELCOME_TEXT = (
    "<b>👋 Привет! Я AllyTaskBot — помощник для задач команды.</b>\n\n"
    "Я собираю идеи и задачи в одном месте, чтобы они не терялись "
    "в переписке. Вот что я умею:\n\n"
    "<b>/add</b> — добавить новую задачу\n"
    "<b>/list</b> — посмотреть все задачи\n"
    "<b>/list_csv</b> — выгрузить все задачи в CSV-файл\n\n"
    "Начни с команды <b>/add</b> 👇"
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Срабатывает при команде /start (и при нажатии кнопки START у бота)."""
    await message.answer(WELCOME_TEXT)