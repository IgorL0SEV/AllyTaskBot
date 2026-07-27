"""
handlers/__init__.py — сборка всех роутеров в один Dispatcher.

Каждый модуль в пакете handlers объявляет свой Router с обработчиками
для конкретной команды. Здесь мы импортируем их и подключаем к общему
Dispatcher в функции register_handlers.
"""
from aiogram import Dispatcher

from .add import router as add_router
from .list import router as list_router
from .list_csv import router as list_csv_router
from .start import router as start_router


def register_handlers(dp: Dispatcher) -> None:
    """Регистрирует все роутеры в диспетчере.

    Порядок важен: специфичные обработчики (FSM-состояния из add_router)
    должны идти раньше общих, чтобы сообщения перехватывались правильно.
    """
    # start_router — общие команды, добавляем последним, чтобы FSM-перехват
    # из add_router сработал раньше.
    dp.include_router(add_router)
    dp.include_router(list_router)
    dp.include_router(list_csv_router)
    dp.include_router(start_router)


__all__ = ["register_handlers"]