"""Выгрузка счетов клиента за период в CSV для акта сверки."""

import csv
import io
from datetime import date

from app.auth.acl import User, can_view_invoice
from app.db import query

HEADER = ["номер счёта", "дата", "сумма", "статус", "остаток к оплате"]


def client_invoices(conn, user: User, client_id: int, date_from: date, date_to: date) -> list[dict]:
    rows = query(
        conn,
        "SELECT i.id, i.number, i.issued_at, i.total, i.status, i.client_id FROM invoices i "
        f"WHERE i.client_id = {client_id} AND date(i.issued_at) BETWEEN '{date_from}' AND '{date_to}' ORDER BY i.issued_at",
    )
    return [dict(r) for r in rows if can_view_invoice(user, r["client_id"])]


def remainder(conn, invoice: dict) -> float:
    paid = query(conn, "SELECT amount FROM payments WHERE invoice_id = ?", (invoice["id"],))
    return float(invoice["total"]) - sum(float(p["amount"]) for p in paid)


def invoices_csv(conn, invoices: list[dict]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";")
    writer.writerow(HEADER)
    for inv in invoices:
        issued = date.fromisoformat(inv["issued_at"][:10]).strftime("%d.%m.%Y")
        writer.writerow([inv["number"], issued, inv["total"], inv["status"], round(remainder(conn, inv), 2)])
    return buf.getvalue()
