"""Оплаты по счетам."""

from datetime import date
from decimal import Decimal

from app.auth.acl import User, scope_sql
from app.db import query

INVOICE_STATUSES = ("issued", "partially_paid", "paid", "cancelled")


def payments_for_invoice(conn, invoice_id: int) -> list[dict]:
    rows = query(conn, "SELECT id, amount, paid_at FROM payments WHERE invoice_id = ? ORDER BY paid_at", (invoice_id,))
    return [{"id": r["id"], "amount": Decimal(r["amount"]), "paid_at": r["paid_at"]} for r in rows]


def invoice_balance(conn, invoice_id: int) -> Decimal:
    invoice = query(conn, "SELECT total FROM invoices WHERE id = ?", (invoice_id,))[0]
    paid = sum((p["amount"] for p in payments_for_invoice(conn, invoice_id)), Decimal("0"))
    return Decimal(invoice["total"]) - paid


def payments_by_day(conn, user: User, day: date) -> list[dict]:
    """Оплаты за день в пределах прав пользователя."""
    where, params = scope_sql(user, "i")
    rows = query(
        conn,
        f"SELECT p.id, p.amount, p.paid_at, i.number, i.client_id FROM payments p "
        f"JOIN invoices i ON i.id = p.invoice_id WHERE date(p.paid_at) = ? AND {where} ORDER BY p.paid_at",
        (day.isoformat(), *params),
    )
    return [dict(r) for r in rows]


def last_payment_date(conn, invoice_id: int) -> str:
    rows = payments_for_invoice(conn, invoice_id)
    return rows[-1]["paid_at"]

