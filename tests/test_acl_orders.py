import pytest

from app.auth.acl import User, can_view_invoice, scope_sql
from app.orders.api import cancel_order_v1
from app.orders.service import TransitionError, change_status


def test_scope_sql_per_role():
    assert scope_sql(User(1, "admin")) == ("1 = 1", ())
    assert scope_sql(User(2, "client", client_id=7)) == ("i.client_id = ?", (7,))
    assert scope_sql(User(3, "manager", managed_clients=frozenset({5, 2}))) == ("i.client_id IN (?, ?)", (2, 5))
    assert scope_sql(User(4, "client")) == ("1 = 0", ())


def test_can_view_invoice():
    assert can_view_invoice(User(3, "manager", managed_clients=frozenset({5})), 5)
    assert not can_view_invoice(User(2, "client", client_id=7), 8)


def test_status_transitions():
    order = {"id": 1, "status": "new", "total": "10", "created_at": "2026-01-01"}
    assert change_status(order, "confirmed")["status"] == "confirmed"
    with pytest.raises(TransitionError):
        change_status(order | {"status": "shipped"}, "cancelled")
    assert cancel_order_v1(order | {"status": "delivered"})[0] == 409
