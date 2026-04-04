from abc import ABC

from sqlinpython.base import CompleteSqlQuery


class SelectStatement(CompleteSqlQuery, ABC):
    """Abstract base for SELECT statements. Isolated to avoid circular imports."""

    pass
