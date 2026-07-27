"""
config.py — конфигурация проекта.

Загружает секретные параметры (токен бота) из файла .env,
чтобы не хранить их прямо в коде и не коммитить в GitHub.
"""
import os
from dotenv import load_dotenv

# Читаем файл .env (если он есть) и кладём его переменные в os.environ
load_dotenv()


class Config:
    """Контейнер с настройками приложения."""

    # Токен Telegram-бота (от @BotFather). Пустая строка по умолчанию,
    # чтобы ниже можно было проверить, что токен действительно задан.
    bot_token: str = os.getenv("BOT_TOKEN", "")

    # Путь к файлу базы данных SQLite. По умолчанию — data/tasks.db.
    # Папка data/ создаётся автоматически в Database.__init__.
    db_path: str = os.getenv("DB_PATH", "data/tasks.db")


# Один общий экземпляр конфига на всё приложение
config = Config()

# Защита от запуска без токена: если .env нет или BOT_TOKEN пустой —
# лучше упасть сразу с понятной ошибкой, чем падать внутри aiogram.
if not config.bot_token:
    raise RuntimeError(
        "BOT_TOKEN не задан. Скопируйте .env.example в .env "
        "и впишите токен от @BotFather."
    )