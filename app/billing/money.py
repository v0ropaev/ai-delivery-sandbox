"""Денежные расчёты: только Decimal, ROUND_HALF_UP (CLAUDE.md, no-go 7)."""

from decimal import ROUND_HALF_UP, Decimal

KOPECK = Decimal("0.01")
VAT_RATE = Decimal("0.20")


def round_money(value: Decimal) -> Decimal:
    return value.quantize(KOPECK, rounding=ROUND_HALF_UP)


def vat_included(total: Decimal) -> Decimal:
    """НДС, включённый в сумму: total * 20 / 120."""
    return round_money(total * VAT_RATE / (1 + VAT_RATE))
