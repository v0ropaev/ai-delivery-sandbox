"""Реестр оплат за день для сверки с банком (CSV, разделитель «;»)."""

import csv
import io
import logging
from datetime import date
from decimal import Decimal

from app.auth.acl import User, scope_sql
from app.billing.money import round_money
from app.db import query

log = logging.getLogger(__name__)
HEADER = ["дата оплаты", "номер счёта", "клиент", "сумма", "статус счёта"]


def registry_rows(conn, user: User, day: date) -> list[dict]:
    """Оплаты за день в пределах прав пользователя; счета в статусе cancelled не попадают в реестр."""
    where, params = scope_sql(user, "i")
    start, end = f"{day.isoformat()} 00:00:00", f"{day.isoformat()} 23:59:59"
    rows = query(
        conn,
        "SELECT p.paid_at, i.number AS invoice, c.name AS client, p.amount, i.status "
        "FROM payments p JOIN invoices i ON i.id = p.invoice_id JOIN clients c ON c.id = i.client_id "
        f"WHERE p.paid_at BETWEEN ? AND ? AND i.status != 'cancelled' AND {where} ORDER BY p.paid_at",
        (start, end, *params),
    )
    log.info("registry: %d payments for %s, user_id=%s", len(rows), day.isoformat(), user.user_id)
    return [dict(r) for r in rows]


def registry_csv(rows: list[dict]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";")
    writer.writerow(HEADER)
    for r in rows:
        paid = date.fromisoformat(r["paid_at"][:10]).strftime("%d.%m.%Y")
        writer.writerow([paid, r["invoice"], r["client"], f"{round_money(Decimal(r['amount'])):.2f}", r["status"]])
    return buf.getvalue()
