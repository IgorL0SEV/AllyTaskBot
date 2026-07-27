"""
handlers/start.py — обработчик команды /start и единый список команд бота.

Чтобы добавить/изменить команду — отредактируйте список COMMANDS ниже.
Текст приветствия и меню Telegram соберутся из него автоматически.
"""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import BotCommand, Message

router = Router(name="start")


# ==================================================================
#   СПИСОК КОМАНД БОТА — меняйте здесь
# ==================================================================
# Формат:  ("команда",  "описание")
#               ↑            ↑
#         без слэша     что увидит пользователь
#
# Порядок строк = порядок в приветствии и в меню Telegram.
# Добавить команду — впишите строку по аналогии.
# Удалить — сотрите строку. (Сам обработчик команды живёт в handlers/*.py.)
COMMANDS = [
    ("add",      "добавить новую задачу"),
    ("list",     "посмотреть все задачи"),
    ("list_csv", "выгрузить все задачи в CSV-файл"),
]
# ==================================================================


# Вступление и концовка приветствия. HTML-разметка разрешена
# (ParseMode.HTML включён в main.py): <b>жирный</b>, <i>курсив</i> и т.д.
INTRO_TEXT = (
    "<b>👋 Привет! Я AllyTaskBot — помощник для задач команды.</b>\n\n"
    "Я собираю идеи и задачи в одном месте, чтобы они не терялись "
    "в переписке. Вот что я умею:\n\n"
)
OUTRO_TEXT = "\n\nНачни с команды <b>/add</b> 👇"


def build_welcome_text() -> str:
    """Собирает текст приветствия из INTRO + списка команд + OUTRO.

    Команды берутся из списка COMMANDS, поэтому при его изменении
    приветствие обновится автоматически.
    """
    lines = [f"<b>/{cmd}</b> — {desc}" for cmd, desc in COMMANDS]
    return INTRO_TEXT + "\n".join(lines) + OUTRO_TEXT


def bot_commands() -> list[BotCommand]:
    """Возвращает список команд для Telegram-меню (кнопка Menu возле ввода)."""
    return [BotCommand(command=cmd, description=desc) for cmd, desc in COMMANDS]


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Срабатывает при команде /start (и при нажатии кнопки START у бота)."""
    await message.answer(build_welcome_text())