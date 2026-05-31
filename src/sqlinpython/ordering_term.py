from abc import ABC
from typing import override

from sqlinpython.base import SqlElement

# SPEC: https://sqlite.org/syntax/ordering-term.html


class OrderingTerm(SqlElement, ABC):
    pass


class OrderingTermWithNulls(OrderingTerm):
    def __init__(self, prev: SqlElement, nulls_first: bool) -> None:
        self._prev = prev
        self._nulls_first = nulls_first

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        if self._nulls_first:
            buffer.append(" NULLS FIRST")
        else:
            buffer.append(" NULLS LAST")


class IHasNulls(OrderingTerm, ABC):
    @property
    def NullsFirst(self) -> OrderingTermWithNulls:
        return OrderingTermWithNulls(self, True)

    @property
    def NullsLast(self) -> OrderingTermWithNulls:
        return OrderingTermWithNulls(self, False)
