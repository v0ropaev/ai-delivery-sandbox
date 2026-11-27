"""Синхронизация заказов со сделками CRM (Битрикс24). Идемпотентно по external_id."""

import logging

log = logging.getLogger(__name__)
STAGE_BY_STATUS = {"new": "NEW", "confirmed": "PREPARATION", "shipped": "EXECUTING", "delivered": "WON", "cancelled": "LOSE"}


def deal_payload(order: dict) -> dict:
    return {
        "ORIGIN_ID": f"order-{order['id']}",  # ключ идемпотентности: повторная синхронизация не создаёт дубль
        "TITLE": f"Заказ {order['number']}",
        "STAGE_ID": STAGE_BY_STATUS[order["status"]],
        "OPPORTUNITY": str(order["total"]),
    }
