from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import CompleteSqlQuery, SqlElement, comma_separated
from sqlinpython.expression import Expression
from sqlinpython.indexed_column import IndexedColumn
from sqlinpython.name import Name

# SPEC: https://sqlite.org/lang_createindex.html


class CreateIndexStatement(CompleteSqlQuery, ABC):
    pass


class CreateIndexWithWhere(CreateIndexStatement):
    def __init__(self, prev: SqlElement, expr: Expression):
        self._prev = prev
        self._expr = expr

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" WHERE ")
        self._expr._create_query(buffer)


class CreateIndexOnTable(CreateIndexStatement):
    def __init__(
        self,
        prev: SqlElement,
        table: Name,
        columns: tuple[IndexedColumn, ...],
    ):
        self._prev = prev
        self._table = table
        self._columns = columns

    def Where(self, expr: Expression) -> CreateIndexWithWhere:
        return CreateIndexWithWhere(self, expr)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ON ")
        self._table._create_query(buffer)
        buffer.append(" (")
        comma_separated(buffer, self._columns)
        buffer.append(")")


class CreateIndexWithName(SqlElement):
    def __init__(self, prev: SqlElement, schema: Name, index: Name | None):
        self._prev = prev
        self._schema = schema
        self._index = index

    def On(
        self,
        table: str | Name,
        *cols: *tuple[IndexedColumn, *tuple[IndexedColumn, ...]],
    ) -> CreateIndexOnTable:
        if isinstance(table, str):
            table = Name(table)
        return CreateIndexOnTable(self, table, cols)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._schema._create_query(buffer)
        if self._index is not None:
            buffer.append(".")
            self._index._create_query(buffer)


class CreateIndexIfNotExists(CreateIndexWithName):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def __call__(
        self, schema: str | Name, index: str | Name | None = None, /
    ) -> CreateIndexWithName:
        if isinstance(schema, str):
            schema = Name(schema)
        if isinstance(index, str):
            index = Name(index)
        return CreateIndexWithName(self, schema, index)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IF NOT EXISTS")


class CreateIndex(CreateIndexIfNotExists):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @property
    def IfNotExists(self) -> CreateIndexIfNotExists:
        return CreateIndexIfNotExists(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" INDEX")
