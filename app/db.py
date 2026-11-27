"""Доступ к базе. Только параметризованные запросы (см. CLAUDE.md, no-go 3)."""

import sqlite3
from contextlib import contextmanager
from typing import Any, Iterator

from app.config import settings


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def query(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...] | dict[str, Any] = ()) -> list[sqlite3.Row]:
    """Выполнить SELECT с параметрами и вернуть все строки."""
    return conn.execute(sql, params).fetchall()


def execute(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...] | dict[str, Any] = ()) -> int:
    cur = conn.execute(sql, params)
    conn.commit()
    return cur.rowcount
