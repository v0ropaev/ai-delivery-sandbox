import sqlite3
from datetime import date
from pathlib import Path

from app.auth.acl import User
from app.reports.invoices_export import client_invoices, invoices_csv

SCHEMA = (Path(__file__).parents[1] / "migrations" / "0001_init.sql").read_text()


def make_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.executescript(
        """
        INSERT INTO invoices (id, number, client_id, total, status, issued_at) VALUES
            (1, 'INV-2026-115', 7, '12000', 'partially_paid', '2026-11-01'),
            (2, 'INV-2026-116', 8, '500', 'issued', '2026-11-02');
        INSERT INTO payments (invoice_id, amount, paid_at) VALUES (1, '10000', '2026-11-05 10:00:00');
        """
    )
    return conn


def test_manager_sees_only_own_clients():
    conn = make_db()
    manager = User(1, "manager", managed_clients=frozenset({7}))
    assert [i["number"] for i in client_invoices(conn, manager, 7, date(2026, 11, 1), date(2026, 11, 30))] == ["INV-2026-115"]
    assert client_invoices(conn, manager, 8, date(2026, 11, 1), date(2026, 11, 30)) == []


def test_csv_format_and_remainder():
    conn = make_db()
    rows = client_invoices(conn, User(9, "accountant"), 7, date(2026, 11, 1), date(2026, 11, 30))
    lines = invoices_csv(conn, rows).strip().splitlines()
    assert lines[1] == "INV-2026-115;01.11.2026;12000.00;partially_paid;2000.00"


def test_empty_period_only_header():
    conn = make_db()
    assert invoices_csv(conn, client_invoices(conn, User(9, "accountant"), 7, date(2025, 1, 1), date(2025, 1, 31))).strip() == (
        "номер счёта;дата;сумма;статус;остаток к оплате"
    )
