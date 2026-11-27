"""Email-уведомления (отправка заглушена для песочницы)."""

import logging

log = logging.getLogger(__name__)

TEMPLATES = {
    "order_created": "Заказ {number} создан и передан менеджеру.",
    "invoice_overdue": "Счёт {number} просрочен. Сумма к оплате: {amount} руб.",
}


def render(template: str, **params) -> str:
    return TEMPLATES[template].format(**params)


def send(to: str, template: str, client_id: int, **params) -> bool:
    body = render(template, **params)
    log.info("email %s queued for client_id=%s", template, client_id)  # без адреса: PII в логах запрещены
    return bool(to and body)
