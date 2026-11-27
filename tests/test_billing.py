from decimal import Decimal

from app.billing.invoices import invoice_summary, invoice_total
from app.billing.money import round_money, vat_included


def test_round_half_up():
    assert round_money(Decimal("10.005")) == Decimal("10.01")


def test_vat_included():
    assert vat_included(Decimal("120.00")) == Decimal("20.00")


def test_invoice_total_with_discount():
    lines = [{"price": "100.10", "qty": 3}, {"price": "50", "qty": 1, "discount": "5.30"}]
    assert invoice_total(lines) == Decimal("345.00")
    assert invoice_summary(lines)["lines"] == 2
