"""
database/db.py — класс Database для работы с SQLite3.

SQLite3 — встроенная в Python база данных. Данные хранятся в одном файле
(по умолчанию data/tasks.db) и не теряются между перезапусками бота.

Внимание: модуль sqlite3 — синхронный. Для MVP этого достаточно (операций мало,
они быстрые). Для масштабирования стоит перейти на aiosqlite — см. README.
"""
import csv
import io
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

# Часовой пояс Минска: UTC+3, без перехода на летнее время.
# Используем фиксированный offset вместо zoneinfo — это не требует
# пакета tzdata, которого по умолчанию нет на Windows.
MINSK_TZ = timezone(timedelta(hours=3))


class Database:
    """Обёртка над соединением SQLite3 для таблицы tasks."""

    def __init__(self, db_path: str = "data/tasks.db") -> None:
        # Сохраняем путь и сразу создаём папку, если её ещё нет,
        # иначе sqlite3 не сможет записать файл.
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

        # check_same_thread=False —允许 aiogram вызывать БД из разных
        # coroutine (потоков в одном event loop). Для MVP безопасно,
        # так как запись идёт через одно соединение.
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        # Чтобы строки возвращались в виде dict-подобных tuple — включаем
        # доступ к колонкам по имени (не используем, но удобно при отладке).
        self.connection.row_factory = sqlite3.Row

        # Режим WAL = Write-Ahead Logging: лучше переносит перезапуски
        # и позволяет читать БД во время записи.
        self.connection.execute("PRAGMA journal_mode=WAL;")

        # Сразу создаём таблицу, если её ещё нет.
        self._create_table()

    # ------------------------------------------------------------------
    # Создание схемы
    # ------------------------------------------------------------------
    def _create_table(self) -> None:
        """Создаёт таблицу tasks, если она не существует.

        Колонки:
          id         — уникальный номер задачи (autoincrement);
          text       — текст задачи/идеи;
          user       — имя пользователя, оставившего задачу;
          created_at — дата и время создания (часовой пояс Минска, UTC+3);
          status     — статус задачи («новое», «в работе», «выполнено»);
          category   — категория («фронт-энд», «бэк-энд», «база данных», «общее»).
        """
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                text       TEXT NOT NULL,
                user       TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status     TEXT DEFAULT 'новое',
                category   TEXT DEFAULT 'общее'
            )
            """
        )
        self.connection.commit()

    # ------------------------------------------------------------------
    # CRUD-методы
    # ------------------------------------------------------------------
    def add_task(self, text: str, user: str, status: str, category: str) -> int:
        """Добавляет новую задачу и возвращает её id.

        created_at вычисляется в Python по часовому поясу Минска (UTC+3),
        а не через CURRENT_TIMESTAMP SQLite (которая отдаёт UTC).
        """
        created_at = datetime.now(MINSK_TZ).strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.connection.execute(
            """
            INSERT INTO tasks (text, user, created_at, status, category)
            VALUES (?, ?, ?, ?, ?)
            """,
            (text, user, created_at, status, category),
        )
        self.connection.commit()
        return cursor.lastrowid  # id новой строки

    def get_all_tasks(self) -> List[Tuple]:
        """Возвращает все задачи, отсортированные по id (по порядку добавления)."""
        cursor = self.connection.execute(
            """
            SELECT id, text, user, created_at, status, category
            FROM tasks
            ORDER BY id ASC
            """
        )
        # fetchall() возвращает список строк (sqlite3.Row), преобразуем к tuple
        return [tuple(row) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Экспорт в CSV
    # ------------------------------------------------------------------
    def export_csv(self) -> io.BytesIO:
        """Выгружает все задачи в CSV и возвращает BytesIO-буфер.

        BytesIO — файлоподобный объект в памяти. Удобно отправить
        прямо в Telegram как документ, не создавая временный файл на диске.
        """
        buffer = io.BytesIO()

        # csv.writer ожидает текстовый поток, а BytesIO — бинарный.
        # Поэтому оборачиваем через io.TextIOWrapper с UTF-8 + BOM:
        # BOM нужен, чтобы Excel/LibreOffice правильно открыли кириллицу.
        wrapper = io.TextIOWrapper(buffer, encoding="utf-8-sig", newline="")

        # Разделитель ";" — чтобы Excel/LibreOffice в русской локали
        # корректно разбивали по колонкам (запятая там — десятичный разделитель).
        writer = csv.writer(wrapper, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        # Заголовок таблицы
        writer.writerow(["id", "text", "user", "created_at", "status", "category"])

        # Данные
        for row in self.get_all_tasks():
            writer.writerow(row)

        # flush, чтобы данные ушли в buffer до чтения
        wrapper.flush()
        wrapper.detach()  # отвязываем, чтобы не закрыть buffer при закрытии wrapper

        # Перематываем в начало — aiogram будет читать с самого начала
        buffer.seek(0)
        return buffer

    # ------------------------------------------------------------------
    # Закрытие соединения
    # ------------------------------------------------------------------
    def close(self) -> None:
        """Закрывает соединение с базой. Вызывать при остановке бота."""
        self.connection.close()