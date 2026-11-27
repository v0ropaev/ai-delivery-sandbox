"""Заказы и статусы."""

STATUSES = ["new", "confirmed", "shipped", "delivered", "cancelled"]
TRANSITIONS = {
    "new": {"confirmed", "cancelled"},
    "confirmed": {"shipped", "cancelled"},
    "shipped": {"delivered"},
    "delivered": set(),
    "cancelled": set(),
}


class TransitionError(ValueError):
    pass


def change_status(order: dict, new_status: str) -> dict:
    current = order["status"]
    if new_status not in TRANSITIONS.get(current, set()):
        raise TransitionError(f"Переход {current} → {new_status} запрещён")
    return order | {"status": new_status}


def can_cancel(order: dict) -> bool:
    return "cancelled" in TRANSITIONS.get(order["status"], set())
