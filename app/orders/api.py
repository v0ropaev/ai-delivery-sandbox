"""Публичный API v1 для партнёров (CLAUDE.md, no-go 6: без breaking changes)."""

from app.orders.service import TransitionError, change_status


def get_order_v1(order: dict) -> dict:
    return {
        "id": order["id"],
        "external_id": order.get("external_id"),
        "status": order["status"],
        "total": str(order["total"]),
        "created_at": order["created_at"],
    }


def cancel_order_v1(order: dict) -> tuple[int, dict]:
    try:
        updated = change_status(order, "cancelled")
    except TransitionError:
        return 409, {"error": "order_cannot_be_cancelled", "order_id": order["id"]}
    return 200, get_order_v1(updated)
