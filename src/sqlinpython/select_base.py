from abc import ABC

from sqlinpython.base import CompleteSqlQuery


class Complete:
    pass


class Core(Complete):
    pass


class SelectStatement_[T: Core | Complete](CompleteSqlQuery, ABC):
    """Abstract base for SELECT statements. Isolated to avoid circular imports."""

    pass


SelectStatement = SelectStatement_[Complete]
