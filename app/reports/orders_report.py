"""Отчёт по заказам за период (CSV)."""

import csv
import io
from datetime import date

from app.db import query
from app.orders.service import STATUSES

COLUMNS = ["number", "client", "manager", "status", "total", "created_at"]


class UnknownStatusError(ValueError):
    pass


def orders_report(conn, date_from: date, date_to: date, status: str | None = None) -> list[dict]:
    """Отчёт по заказам за период; status — необязательный фильтр по статусу заказа."""
    if status is not None and status not in STATUSES:
        raise UnknownStatusError(f"Неизвестный статус «{status}». Допустимые: {', '.join(STATUSES)}.")
    sql = (
        "SELECT o.number, c.name AS client, m.name AS manager, o.status, o.total, o.created_at "
        "FROM orders o JOIN clients c ON c.id = o.client_id LEFT JOIN users m ON m.id = c.manager_id "
        "WHERE date(o.created_at) BETWEEN ? AND ?"
    )
    params: tuple = (date_from.isoformat(), date_to.isoformat())
    if status is not None:
        sql += " AND o.status = ?"
        params += (status,)
    rows = query(conn, sql + " ORDER BY o.created_at", params)
    return [dict(r) for r in rows]


def to_csv(rows: list[dict], columns: list[str] = COLUMNS) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, delimiter=";", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()
