"""Счета."""

from decimal import Decimal

from app.billing.money import round_money, vat_included


def invoice_total(lines: list[dict]) -> Decimal:
    """Сумма счёта по строкам: цена × количество − скидка строки."""
    total = Decimal("0")
    for line in lines:
        total += Decimal(line["price"]) * int(line["qty"]) - Decimal(line.get("discount", "0"))
    return round_money(total)


def invoice_summary(lines: list[dict]) -> dict:
    total = invoice_total(lines)
    return {"total": total, "vat": vat_included(total), "lines": len(lines)}
