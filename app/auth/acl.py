"""Права доступа. Фильтрация — в запросе (pre-retrieval), см. CLAUDE.md, no-go 4."""

from dataclasses import dataclass, field

ROLES = {"client", "manager", "accountant", "admin"}


@dataclass(frozen=True)
class User:
    user_id: int
    role: str
    client_id: int | None = None  # для роли client — чьи данные видит
    managed_clients: frozenset[int] = field(default_factory=frozenset)  # для роли manager


def scope_sql(user: User, alias: str = "i") -> tuple[str, tuple]:
    """Условие WHERE, ограничивающее выборку счетов правами пользователя.

    Возвращает фрагмент SQL с плейсхолдерами и параметры к нему.
    """
    if user.role in ("admin", "accountant"):
        return "1 = 1", ()
    if user.role == "client" and user.client_id is not None:
        return f"{alias}.client_id = ?", (user.client_id,)
    if user.role == "manager" and user.managed_clients:
        marks = ", ".join("?" for _ in user.managed_clients)
        return f"{alias}.client_id IN ({marks})", tuple(sorted(user.managed_clients))
    return "1 = 0", ()


def can_view_invoice(user: User, client_id: int) -> bool:
    if user.role in ("admin", "accountant"):
        return True
    if user.role == "client":
        return user.client_id == client_id
    if user.role == "manager":
        return client_id in user.managed_clients
    return False
