from __future__ import annotations

import typing
from abc import ABC
from typing import override

from sqlinpython.base import CompleteSqlQuery, SqlElement, comma_separated
from sqlinpython.column_definition import ColumnDefinition
from sqlinpython.name import Name
from sqlinpython.select_base import SelectStatement
from sqlinpython.table_constraint import TableConstraint


# SPEC: https://sqlite.org/syntax/create-table-stmt.html
class CreateTableStatement(CompleteSqlQuery, ABC):
    pass


class CreateTableAs(CreateTableStatement):
    def __init__(self, prev: SqlElement, select_stmt: SelectStatement):
        self._prev = prev
        self._select_stmt = select_stmt

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" AS ")
        self._select_stmt._create_query(buffer)


class ITableOptions(CreateTableStatement, ABC):
    @property
    def WithoutRowId(self) -> CreateTableWithOptions:
        return CreateTableWithOptions(self, "WITHOUT ROWID")

    @property
    def Strict(self) -> CreateTableWithOptions:
        return CreateTableWithOptions(self, "STRICT")


class CreateTableWithOptions(ITableOptions):
    def __init__(
        self, prev: SqlElement, option: typing.Literal["WITHOUT ROWID", "STRICT"]
    ):
        self._prev = prev
        self._option = option

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        if isinstance(self._prev, CreateTableWithOptions):
            buffer.append(",")
        buffer.append(f" {self._option}")


class CreateTableWithDefinitions(ITableOptions):
    def __init__(
        self, prev: SqlElement, args: tuple[ColumnDefinition | TableConstraint, ...]
    ):
        self._prev = prev
        self._args = args

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" (")
        comma_separated(buffer, self._args)
        buffer.append(")")


class CreateTableWithName(SqlElement):
    def __init__(self, prev: SqlElement, schema: Name, table: Name | None):
        self._prev = prev
        self._schema = schema
        self._table = table

    def As(self, select_stmt: SelectStatement) -> CreateTableAs:
        return CreateTableAs(self, select_stmt)

    def __call__(
        self,
        *definitions: *tuple[
            ColumnDefinition, *tuple[ColumnDefinition | TableConstraint, ...]
        ],
    ) -> CreateTableWithDefinitions:
        seen_constraint = False
        for defn in definitions:
            if isinstance(defn, TableConstraint):
                seen_constraint = True
            elif seen_constraint:
                raise ValueError(
                    "column definitions must come before table constraints"
                )
        return CreateTableWithDefinitions(self, definitions)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._schema._create_query(buffer)
        if self._table is not None:
            buffer.append(".")
            self._table._create_query(buffer)


class CreateTableIfNotExists(SqlElement):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def __call__(
        self, schema: str | Name, table: str | Name | None = None, /
    ) -> CreateTableWithName:
        if isinstance(schema, str):
            schema = Name(schema)
        if isinstance(table, str):
            table = Name(table)
        return CreateTableWithName(self, schema, table)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IF NOT EXISTS")


class CreateTable(CreateTableIfNotExists):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @property
    def IfNotExists(self) -> CreateTableIfNotExists:
        return CreateTableIfNotExists(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" TABLE")
