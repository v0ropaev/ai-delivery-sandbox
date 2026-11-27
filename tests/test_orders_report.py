import sqlite3
from datetime import date
from pathlib import Path

import pytest

from app.reports.orders_report import UnknownStatusError, orders_report

SCHEMA = (Path(__file__).parents[1] / "migrations" / "0001_init.sql").read_text()


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    c.executescript(
        """
        INSERT INTO clients (id, name) VALUES (1, 'ООО Ромашка');
        INSERT INTO orders (id, number, client_id, status, total, created_at) VALUES
            (1, 'A-1', 1, 'shipped', '100', '2026-11-03'),
            (2, 'A-2', 1, 'new', '50', '2026-11-04'),
            (3, 'A-3', 1, 'shipped', '70', '2026-12-01');
        """
    )
    return c


def test_filter_by_status(conn):
    rows = orders_report(conn, date(2026, 11, 1), date(2026, 11, 30), status="shipped")
    assert [r["number"] for r in rows] == ["A-1"]


def test_without_status_all_orders(conn):
    rows = orders_report(conn, date(2026, 11, 1), date(2026, 11, 30))
    assert [r["number"] for r in rows] == ["A-1", "A-2"]


def test_unknown_status_raises_readable_error(conn):
    with pytest.raises(UnknownStatusError, match="Неизвестный статус «lost»"):
        orders_report(conn, date(2026, 11, 1), date(2026, 11, 30), status="lost")
