from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.name import Name

# SPEC: https://sqlite.org/lang_createvtab.html


class CreateVirtualTableStatement(CompleteSqlQuery, ABC):
    pass


class CreateVirtualTableWithArgs(CreateVirtualTableStatement):
    def __init__(self, prev: SqlElement, args: tuple[str, ...]):
        self._prev = prev
        self._args = args

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append("(")
        for i, arg in enumerate(self._args):
            if i > 0:
                buffer.append(", ")
            buffer.append(arg)
        buffer.append(")")


class CreateVirtualTableUsing(CreateVirtualTableStatement):
    def __init__(self, prev: SqlElement, module: Name):
        self._prev = prev
        self._module = module

    def __call__(self, *args: str) -> CreateVirtualTableWithArgs:
        return CreateVirtualTableWithArgs(self, args)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" USING ")
        self._module._create_query(buffer)


class CreateVirtualTableWithName(SqlElement):
    def __init__(self, prev: SqlElement, schema: Name, table: Name | None):
        self._prev = prev
        self._schema = schema
        self._table = table

    def Using(self, module: str | Name) -> CreateVirtualTableUsing:
        if isinstance(module, str):
            module = Name(module)
        return CreateVirtualTableUsing(self, module)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._schema._create_query(buffer)
        if self._table is not None:
            buffer.append(".")
            self._table._create_query(buffer)


class CreateVirtualTableIfNotExists(SqlElement):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def __call__(
        self, schema: str | Name, table: str | Name | None = None, /
    ) -> CreateVirtualTableWithName:
        if isinstance(schema, str):
            schema = Name(schema)
        if isinstance(table, str):
            table = Name(table)
        return CreateVirtualTableWithName(self, schema, table)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IF NOT EXISTS")


class CreateVirtualTable(CreateVirtualTableIfNotExists):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @property
    def IfNotExists(self) -> CreateVirtualTableIfNotExists:
        return CreateVirtualTableIfNotExists(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" VIRTUAL TABLE")
