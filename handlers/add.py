"""
handlers/add.py — команда /add и FSM-сценарий добавления задачи.

FSM (Finite State Machine) — машина состояний. Сценарий /add состоит
из шагов: ввод текста -> выбор категории -> выбор статуса -> сохранение.
На каждом шаге бот «помнит», что уже ввёл пользователь, через FSMContext.

Поток:
  1. /add          -> состояние waiting_for_text, спрашиваем текст.
  2. текст         -> сохраняем в state, показываем клавиатуру категорий,
                     переход в waiting_for_category.
  3. категория     -> сохраняем, показываем клавиатуру статусов,
                     переход в waiting_for_status.
  4. статус        -> достаём всё из state, пишем в БД, выходим из FSM.
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
    await message.answer(
        "✍️ <b>Добавление задачи</b>\n\n"
        "Введите текст задачи (идею) одним сообщением:"
    )


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
        "📁 Выберите категорию задачи:",
        reply_markup=categories_keyboard(),
    )


# ---------------------------------------------------------------------
# Шаг 3: ловим категорию, предлагаем статусы
# ---------------------------------------------------------------------
@router.callback_query(AddTask.waiting_for_category, F.data.startswith("category:"))
async def process_category(callback: CallbackQuery, state: FSMContext) -> None:
    """Сохраняет выбранную категорию и показывает кнопки выбора статуса."""
    # callback.data имеет вид "category:front" — отрезаем префикс.
    category_key = callback.data.split(":", 1)[1]
    await state.update_data(category=category_key)

    await callback.message.edit_text(  # меняем предыдущее сообщение
        f"📁 Категория: <b>{get_category_label(category_key)}</b>\n\n"
        f"🚦 Выберите статус задачи:",
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
        await callback.message.edit_text(
            "⚠️ Что-то пошло не так — данные устарели. Попробуйте /add заново."
        )
        await callback.answer()
        return

    # Пишем в базу. В БД храним человекочитаемые подписи, чтобы
    # /list и CSV читались без дополнительных преобразований.
    task_id = db.add_task(
        text=data["text"],
        user=data["user"],
        status=get_status_label(status_key),
        category=get_category_label(data["category"]),
    )

    # Выходим из FSM — сценарий завершён.
    await state.clear()
    await callback.message.edit_text(
        f"✅ <b>Задача #{task_id} добавлена!</b>\n\n"
        f"📝 {data['text']}\n\n"
        f"👤 {data['user']}\n"
        f"📁 {get_category_label(data['category'])}\n"
        f"🚦 {get_status_label(status_key)}\n\n"
        f"Посмотреть все задачи: /list"
    )
    await callback.answer()