"""
handlers/add.py — команда /add и FSM-сценарий добавления задачи.

FSM (Finite State Machine) — машина состояний. Сценарий /add состоит
из шагов: ввод текста -> выбор категории -> выбор статуса -> сохранение.
На каждом шаге бот «помнит», что уже ввёл пользователь, через FSMContext.

Поток:
  1. /add          -> состояние waiting_for_text, спрашиваем текст (Меню 5).
  2. текст         -> сохраняем в state, показываем клавиатуру категорий
                     (Меню 1), переход в waiting_for_category (Меню 6).
  3. категория     -> сохраняем, показываем клавиатуру статусов (Меню 2),
                     переход в waiting_for_status (Меню 7).
  4. статус        -> достаём всё из state, пишем в БД, выходим из FSM
                     (Меню 8 — успех, Меню 9 — ошибка устаревания).

Все тексты сообщений живут в menus.py. Здесь только логика сценария.
"""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from database.db import Database
from handlers.keyboards import (
    categories_keyboard,
    statuses_keyboard,
    get_category_label,
    get_status_label,
)
from menus import (
    MENU_5_ADD_PROMPT,
    MENU_6_CATEGORY_PROMPT,
    MENU_7_STATUS_PROMPT,
    MENU_8_SUCCESS,
    MENU_9_ERROR,
)

router = Router(name="add")


class AddTask(StatesGroup):
    """Состояния сценария добавления задачи."""

    waiting_for_text = State()        # ждём текст задачи от пользователя
    waiting_for_category = State()    # ждём выбор категории (inline-кнопка)
    waiting_for_status = State()       # ждём выбор статуса (inline-кнопка)


def _display_user(message: Message) -> str:
    """Возвращает имя пользователя для сохранения в БД.

    Предпочитаем @username; если его нет (редко), берём имя+фамилию.
    Это и обеспечивает «поддержку множественных пользователей» —
    каждая задача помечается автором.
    """
    user = message.from_user
    if user.username:
        return f"@{user.username}"
    return (user.full_name or "аноним").strip()


# ---------------------------------------------------------------------
# Шаг 1: /add — начало сценария
# ---------------------------------------------------------------------
@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext) -> None:
    """Запускает сценарий: переводит бота в ожидание текста задачи."""
    # На старте сбрасываем любые прежние состояния, чтобы не запутаться.
    await state.clear()
    await state.set_state(AddTask.waiting_for_text)
    await message.answer(MENU_5_ADD_PROMPT)


# ---------------------------------------------------------------------
# Шаг 2: ловим текст, предлагаем категории
# ---------------------------------------------------------------------
@router.message(AddTask.waiting_for_text, F.text, ~F.text.startswith("/"))
async def process_text(message: Message, state: FSMContext) -> None:
    """Сохраняет текст в state и показывает кнопки выбора категории."""
    # Сохраняем текст и сразу имя автора (на случай, если пользователь
    # дальше не пришлёт новых сообщений — мы уже знаем, кто он).
    await state.update_data(text=message.text, user=_display_user(message))
    await state.set_state(AddTask.waiting_for_category)
    await message.answer(
        MENU_6_CATEGORY_PROMPT,
        reply_markup=categories_keyboard(),
    )


# ---------------------------------------------------------------------
# Шаг 3: ловим категорию, предлагаем статусы
# ---------------------------------------------------------------------
@router.callback_query(AddTask.waiting_for_category, F.data.startswith("category:"))
async def process_category(callback: CallbackQuery, state: FSMContext) -> None:
    """Сохраняет выбранную категорию и показывает кнопки выбора статуса."""
    # callback.data имеет вид "category:project1" — отрезаем префикс.
    category_key = callback.data.split(":", 1)[1]
    await state.update_data(category=category_key)
    # Переключаемся в состояние ожидания статуса — без этого клик по
    # кнопке статуса ниже не будет перехвачен этим роутером.
    await state.set_state(AddTask.waiting_for_status)

    await callback.message.edit_text(  # меняем предыдущее сообщение
        MENU_7_STATUS_PROMPT.format(category=get_category_label(category_key)),
        reply_markup=statuses_keyboard(),
    )
    # Подтверждаем callback, чтобы у кнопки не осталось «часиков».
    await callback.answer()


# ---------------------------------------------------------------------
# Шаг 4: ловим статус, сохраняем задачу в БД
# ---------------------------------------------------------------------
@router.callback_query(AddTask.waiting_for_status, F.data.startswith("status:"))
async def process_status(callback: CallbackQuery, state: FSMContext, db: Database) -> None:
    """Достаёт все данные из state, сохраняет задачу в БД и выходит из FSM.

    db: Database — внедрение зависимости: aiogram подставит сюда объект
    Database, который мы положили в main.py как dp["db"] = ...
    """
    status_key = callback.data.split(":", 1)[1]
    data = await state.get_data()  # dict с text, user, category

    # Если вдруг данные потерялись (пользователь долго не отвечал и state
    # устарел) — просим начать заново.
    if not data.get("text"):
        await state.clear()
        await callback.message.edit_text(MENU_9_ERROR)
        await callback.answer()
        return

    # Пишем в базу. В БД храним человекочитаемые подписи, чтобы
    # /list и CSV читались без дополнительных преобразований.
    category_label = get_category_label(data["category"])
    status_label = get_status_label(status_key)
    task_id = db.add_task(
        text=data["text"],
        user=data["user"],
        status=status_label,
        category=category_label,
    )

    # Выходим из FSM — сценарий завершён.
    await state.clear()
    await callback.message.edit_text(
        MENU_8_SUCCESS.format(
            task_id=task_id,
            text=data["text"],
            user=data["user"],
            category=category_label,
            status=status_label,
        )
    )
    await callback.answer()