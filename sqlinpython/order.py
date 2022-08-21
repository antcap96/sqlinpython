from __future__ import annotations

from abc import ABCMeta

from sqlinpython.base import SqlElement


class Order(SqlElement, metaclass=ABCMeta):
    pass


class OrderWithNulls(Order):
    def __init__(self, prev: SqlElement, order: bool) -> None:
        self._prev = prev
        self._order = order

    def _create_query(self) -> str:
        if self._order:
            order = "FIRST"
        else:
            order = "LAST"
        return f"{self._prev._create_query()} NULLS {order}"


class OrderWithAscDesc(OrderWithNulls):
    def __init__(self, prev: SqlElement, ascending: bool) -> None:
        self._prev = prev
        self._ascending = ascending

    def _create_query(self) -> str:
        if self._ascending:
            order = "ASC"
        else:
            order = "DESC"
        return f"{self._prev._create_query()} {order}"

    @property
    def NullsFirst(self) -> OrderWithNulls:
        return OrderWithNulls(self, True)

    @property
    def NullsLast(self) -> OrderWithNulls:
        return OrderWithNulls(self, False)
