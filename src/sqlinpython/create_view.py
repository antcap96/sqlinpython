from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import CompleteSqlQuery, SqlElement, comma_separated
from sqlinpython.name import Name
from sqlinpython.select_base import SelectStatement

# SPEC: https://sqlite.org/lang_createview.html


class CreateViewStatement(CompleteSqlQuery, ABC):
    pass


class CreateViewAs(CreateViewStatement):
    def __init__(self, prev: SqlElement, select_stmt: SelectStatement):
        self._prev = prev
        self._select_stmt = select_stmt

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" AS ")
        self._select_stmt._create_query(buffer)


class CreateViewWithColumns(SqlElement):
    def __init__(self, prev: SqlElement, columns: tuple[Name, ...]):
        self._prev = prev
        self._columns = columns

    def As(self, select_stmt: SelectStatement) -> CreateViewAs:
        return CreateViewAs(self, select_stmt)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" (")
        comma_separated(buffer, self._columns)
        buffer.append(")")


class CreateViewWithName(SqlElement):
    def __init__(self, prev: SqlElement, schema: Name, view: Name | None):
        self._prev = prev
        self._schema = schema
        self._view = view

    def As(self, select_stmt: SelectStatement) -> CreateViewAs:
        return CreateViewAs(self, select_stmt)

    def __call__(
        self,
        *columns: *tuple[Name | str, *tuple[Name | str, ...]],
    ) -> CreateViewWithColumns:
        resolved = tuple(c if isinstance(c, Name) else Name(c) for c in columns)
        return CreateViewWithColumns(self, resolved)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._schema._create_query(buffer)
        if self._view is not None:
            buffer.append(".")
            self._view._create_query(buffer)


class CreateViewIfNotExists(SqlElement):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def __call__(
        self, schema: str | Name, view: str | Name | None = None, /
    ) -> CreateViewWithName:
        if isinstance(schema, str):
            schema = Name(schema)
        if isinstance(view, str):
            view = Name(view)
        return CreateViewWithName(self, schema, view)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IF NOT EXISTS")


class CreateView(CreateViewIfNotExists):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @property
    def IfNotExists(self) -> CreateViewIfNotExists:
        return CreateViewIfNotExists(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" VIEW")
