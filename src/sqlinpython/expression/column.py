from __future__ import annotations

from typing import overload, override

from sqlinpython.name import Name

from .core import Expression12


class ColumnName(Name, Expression12):
    """Expression atom referring to a column. Use ColumnDef for column definitions."""


class TableColumnName(Expression12):
    def __init__(self, table: Name | str, column: Name | str) -> None:
        if isinstance(table, str):
            table = Name(table)
        if isinstance(column, str):
            column = Name(column)
        self._table = table
        self._column = column

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._table._create_query(buffer)
        buffer.append(".")
        self._column._create_query(buffer)


class SchemaTableColumnName(Expression12):
    def __init__(
        self, schema: Name | str, table: Name | str, column: Name | str
    ) -> None:
        if isinstance(schema, str):
            schema = Name(schema)
        if isinstance(table, str):
            table = Name(table)
        if isinstance(column, str):
            column = Name(column)
        self._schema = schema
        self._table = table
        self._column = column

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._schema._create_query(buffer)
        buffer.append(".")
        self._table._create_query(buffer)
        buffer.append(".")
        self._column._create_query(buffer)


@overload
def col(__schema: str, __table: str, __column: str) -> SchemaTableColumnName: ...
@overload
def col(__table: str, __column: str) -> TableColumnName: ...
@overload
def col(__column: str) -> ColumnName: ...
def col(
    n1: str, n2: str | None = None, n3: str | None = None, /
) -> SchemaTableColumnName | TableColumnName | ColumnName:
    if n2 is None:
        return ColumnName(n1)
    if n3 is None:
        return TableColumnName(n1, n2)
    return SchemaTableColumnName(n1, n2, n3)
