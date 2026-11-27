"""Выгрузка счетов клиента за период в CSV для акта сверки."""

import csv
import io
from datetime import date
from decimal import Decimal

from app.auth.acl import User, scope_sql
from app.billing.money import round_money
from app.db import query

HEADER = ["номер счёта", "дата", "сумма", "статус", "остаток к оплате"]


def client_invoices(conn, user: User, client_id: int, date_from: date, date_to: date) -> list[dict]:
    """Счета клиента за период в пределах прав пользователя: права проверяются в запросе (pre-retrieval)."""
    where, params = scope_sql(user, "i")
    rows = query(
        conn,
        "SELECT i.id, i.number, i.issued_at, i.total, i.status FROM invoices i "
        f"WHERE i.client_id = ? AND date(i.issued_at) BETWEEN ? AND ? AND {where} ORDER BY i.issued_at",
        (client_id, date_from.isoformat(), date_to.isoformat(), *params),
    )
    return [dict(r) for r in rows]


def remainder(conn, invoice: dict) -> Decimal:
    paid = query(conn, "SELECT amount FROM payments WHERE invoice_id = ?", (invoice["id"],))
    return round_money(Decimal(invoice["total"]) - sum((Decimal(p["amount"]) for p in paid), Decimal("0")))


def invoices_csv(conn, invoices: list[dict]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";")
    writer.writerow(HEADER)
    for inv in invoices:
        issued = date.fromisoformat(inv["issued_at"][:10]).strftime("%d.%m.%Y")
        total = round_money(Decimal(inv["total"]))
        writer.writerow([inv["number"], issued, f"{total:.2f}", inv["status"], f"{remainder(conn, inv):.2f}"])
    return buf.getvalue()
