import sqlite3
from datetime import date
from pathlib import Path

from app.auth.acl import User
from app.reports.payments_registry import registry_csv, registry_rows

SCHEMA = (Path(__file__).parents[1] / "migrations" / "0001_init.sql").read_text()


def make_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.executescript(
        """
        INSERT INTO clients (id, name) VALUES (1, 'ООО Ромашка'), (2, 'ООО Лютик');
        INSERT INTO invoices (id, number, client_id, total, status, issued_at) VALUES
            (10, 'INV-2026-115', 1, '12000.00', 'paid', '2026-11-01'),
            (11, 'INV-2026-116', 2, '500.00', 'paid', '2026-11-01'),
            (12, 'INV-2026-117', 1, '300.00', 'cancelled', '2026-11-01');
        INSERT INTO payments (invoice_id, amount, paid_at) VALUES
            (10, '12000', '2026-11-05 10:00:00'),
            (11, '500.5', '2026-11-05 11:00:00'),
            (12, '300', '2026-11-05 12:00:00'),
            (10, '1', '2026-11-06 09:00:00');
        """
    )
    return conn


def test_registry_respects_acl_day_and_cancelled():
    rows = registry_rows(make_db(), User(1, "client", client_id=1), date(2026, 11, 5))
    assert [r["invoice"] for r in rows] == ["INV-2026-115"]


def test_registry_csv_format():
    rows = registry_rows(make_db(), User(9, "accountant"), date(2026, 11, 5))
    lines = registry_csv(rows).strip().splitlines()
    assert lines[0] == "дата оплаты;номер счёта;клиент;сумма;статус счёта"
    assert lines[1] == "05.11.2026;INV-2026-115;ООО Ромашка;12000.00;paid"
    assert lines[2] == "05.11.2026;INV-2026-116;ООО Лютик;500.50;paid"


def test_registry_empty_day():
    assert registry_rows(make_db(), User(9, "accountant"), date(2026, 1, 1)) == []
    assert registry_csv([]).strip() == "дата оплаты;номер счёта;клиент;сумма;статус счёта"


def test_export_registry_file():
    from app.reports.payments_registry import export_registry

    name, data = export_registry(make_db(), User(9, "accountant"), date(2026, 11, 5))
    assert name == "payments_2026-11-05.csv"
    assert data.decode("utf-8-sig").splitlines()[1] == "05.11.2026;INV-2026-115;ООО Ромашка;12000.00;paid"
