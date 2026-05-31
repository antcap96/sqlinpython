from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import SqlElement
from sqlinpython.ordering_term import IHasNulls

# SPEC: https://sqlite.org/syntax/indexed-column.html


class IndexedColumn(SqlElement, ABC):
    pass


class IHasAscDesc(IndexedColumn, IHasNulls, ABC):
    @property
    def Asc(self) -> ColumnNameWithOrdering:
        return ColumnNameWithOrdering(self, True)

    @property
    def Desc(self) -> ColumnNameWithOrdering:
        return ColumnNameWithOrdering(self, False)


class ColumnNameWithOrdering(IHasAscDesc):
    def __init__(self, prev: SqlElement, asc: bool) -> None:
        self._prev = prev
        self._asc = asc

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        asc_desc = " ASC" if self._asc else " DESC"
        buffer.append(asc_desc)
