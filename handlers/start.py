"""
handlers/start.py — обработчик команды /start.

Текст приветствия и список команд живут в menus.py (Меню 3 и Меню 4).
Здесь только сборка приветствия из частей и регистрация команд в
Telegram-меню. Чтобы добавить/изменить команду — правьте menus.MENU_4_COMMANDS.
"""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import BotCommand, Message

from menus import MENU_3_INTRO, MENU_3_OUTRO, MENU_4_COMMANDS

router = Router(name="start")


def build_welcome_text() -> str:
    """Собирает текст приветствия: INTRO + строки команд + OUTRO.

    Строки команд берутся из menus.MENU_4_COMMANDS, поэтому при его
    изменении приветствие обновится автоматически.
    """
    lines = [f"<b>/{cmd}</b> — {desc}" for cmd, desc in MENU_4_COMMANDS]
    return MENU_3_INTRO + "\n".join(lines) + MENU_3_OUTRO


def bot_commands() -> list[BotCommand]:
    """Возвращает список команд для Telegram-меню (кнопка Menu возле ввода)."""
    return [BotCommand(command=cmd, description=desc) for cmd, desc in MENU_4_COMMANDS]


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Срабатывает при команде /start (и при нажатии кнопки START у бота)."""
    await message.answer(build_welcome_text())