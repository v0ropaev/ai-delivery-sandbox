"""Отчёт по заказам за период (CSV)."""

import csv
import io
from datetime import date

from app.db import query

COLUMNS = ["number", "client", "manager", "status", "total", "created_at"]


def orders_report(conn, date_from: date, date_to: date) -> list[dict]:
    rows = query(
        conn,
        "SELECT o.number, c.name AS client, m.name AS manager, o.status, o.total, o.created_at "
        "FROM orders o JOIN clients c ON c.id = o.client_id LEFT JOIN users m ON m.id = c.manager_id "
        "WHERE date(o.created_at) BETWEEN ? AND ? ORDER BY o.created_at",
        (date_from.isoformat(), date_to.isoformat()),
    )
    return [dict(r) for r in rows]


def to_csv(rows: list[dict], columns: list[str] = COLUMNS) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, delimiter=";", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()
