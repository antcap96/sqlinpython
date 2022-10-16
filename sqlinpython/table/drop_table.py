from __future__ import annotations

from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.table.table_spec import TableRef


class DropTableWithCascade(CompleteSqlQuery):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} CASCADE"


class DropTableWithTableRef(DropTableWithCascade):
    def __init__(self, prev: SqlElement, table_ref: TableRef) -> None:
        self._prev = prev
        self._table_ref = table_ref

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._table_ref._create_query()}"

    @property
    def Cascade(self) -> DropTableWithCascade:
        return DropTableWithCascade(self)


class DropTableWithIfExists(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} IF EXISTS"

    def __call__(self, table_ref: TableRef) -> DropTableWithTableRef:
        return DropTableWithTableRef(self, table_ref)


class DropTableKeyword(DropTableWithIfExists):
    def __init__(self) -> None:
        pass

    def _create_query(self) -> str:
        return "DROP TABLE"

    @property
    def IfExists(self) -> DropTableWithIfExists:
        return DropTableWithIfExists(self)


DropTable = DropTableKeyword()
