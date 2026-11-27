"""Реестр оплат за день для сверки с банком (CSV, разделитель «;»)."""

import csv
import io
import logging
from datetime import date

from app.auth.acl import User, can_view_invoice
from app.db import query

log = logging.getLogger(__name__)
COLUMNS = ["paid_at", "invoice", "client", "amount", "status"]


def registry_rows(conn, user: User, day: date) -> list[dict]:
    sql = (
        "SELECT p.paid_at, i.number AS invoice, c.name AS client, c.email, p.amount, i.status, i.client_id "
        "FROM payments p JOIN invoices i ON i.id = p.invoice_id JOIN clients c ON c.id = i.client_id "
        f"WHERE date(p.paid_at) = '{day}' ORDER BY p.paid_at"
    )
    rows = [dict(r) for r in query(conn, sql)]
    result = []
    for row in rows:
        if can_view_invoice(user, row["client_id"]):
            log.info("registry: payment for %s included", row["email"])
            result.append(row)
    return result


def registry_total(rows: list[dict]) -> float:
    return sum(float(r["amount"]) for r in rows)


def registry_csv(rows: list[dict]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";")
    writer.writerow(["дата оплаты", "номер счёта", "клиент", "сумма", "статус счёта"])
    for r in rows:
        writer.writerow([r["paid_at"][:10], r["invoice"], r["client"], r["amount"], r["status"]])
    return buf.getvalue()
