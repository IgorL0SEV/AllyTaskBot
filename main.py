"""
main.py — точка входа Telegram-бота AllyTaskBot.

Инициализирует бот (Bot), диспетчер (Dispatcher), базу данных (Database)
и запускает long-polling — бот сам опрашивает Telegram о новых сообщениях.
"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from database.db import Database
from handlers import register_handlers
from handlers.start import bot_commands


async def main() -> None:
    """Главная async-функция: настраивает бота и запускает polling."""
    # Логируем в stdout, чтобы видеть, что происходит.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )
    log = logging.getLogger("allytaskbot")

    # Создаём объект бота. ParseMode.HTML разрешает <b>, <i> и т.д. в ответах.
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Dispatcher — маршрутизатор сообщений. MemoryStorage хранит
    # FSM-состояния в оперативной памяти (достаточно для MVP).
    dp = Dispatcher(storage=MemoryStorage())

    # Внедрение зависимости: объект Database будет доступен в обработчиках
    # как параметр `db: Database` (aiogram подставляет его автоматически).
    db = Database(config.db_path)
    dp["db"] = db

    # Подключаем все роутеры из пакета handlers.
    register_handlers(dp)

    # Регистрируем команды в Telegram-меню (кнопка Menu слева от ввода).
    # Список берётся из handlers/start.py → COMMANDS.
    await bot.set_my_commands(bot_commands())

    log.info("Бот запущен. Polling started...")
    try:
        # start_polling блокирует поток до остановки (Ctrl+C).
        await dp.start_polling(bot)
    finally:
        # При выходе — аккуратно закрываем соединение с БД.
        db.close()
        log.info("Бот остановлен, соединение с БД закрыто.")


if __name__ == "__main__":
    # Запускаем event-loop. KeyboardInterrupt (Ctrl+C) обрабатывается
    # asyncio.run корректно.
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Остановлено пользователем.")