from __future__ import annotations

from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.name import Name


class DropTableComplete(CompleteSqlQuery):
    def __init__(self, prev: SqlElement, schema: Name, table: Name | None) -> None:
        self._prev = prev
        self._schema = schema
        self._table = table

    def _create_query(self) -> str:
        if self._table is None:
            return f"{self._prev._create_query()} {self._schema._create_query()}"
        else:
            return f"{self._prev._create_query()} {self._schema._create_query()}.{self._table._create_query()}"


class DropTableWithIfExists(SqlElement):
    def __init__(self, prev: DropTableKeyword) -> None:
        self._prev = prev

    def __call__(
        # TODO: Consider specific TableName and SchemaName
        self,
        schema: Name | str,
        table: Name | str | None = None,
        /,
    ) -> DropTableComplete:
        if isinstance(schema, str):
            schema = Name(schema)
        if isinstance(table, str):
            table = Name(table)
        return DropTableComplete(self, schema, table)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} IF EXISTS"


class DropTableKeyword(DropTableWithIfExists):
    def __init__(self) -> None:
        pass

    @property
    def IfExists(self) -> DropTableWithIfExists:
        return DropTableWithIfExists(self)

    def _create_query(self) -> str:
        return "DROP TABLE"


DropTable = DropTableKeyword()
