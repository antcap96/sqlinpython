from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import CompleteSqlQuery, SqlElement
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
        for i, col in enumerate(self._columns):
            if i > 0:
                buffer.append(", ")
            col._create_query(buffer)
        buffer.append(")")


class CreateViewWithName(SqlElement):
    def __init__(self, prev: SqlElement, schema_name: Name, view_name: Name | None):
        self._prev = prev
        self._schema_name = schema_name
        self._view_name = view_name

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
        self._schema_name._create_query(buffer)
        if self._view_name is not None:
            buffer.append(".")
            self._view_name._create_query(buffer)


class CreateViewIfNotExists(SqlElement):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def __call__(
        self, schema_name: str | Name, view_name: str | Name | None = None
    ) -> CreateViewWithName:
        if isinstance(schema_name, str):
            schema_name = Name(schema_name)
        if isinstance(view_name, str):
            view_name = Name(view_name)
        return CreateViewWithName(self, schema_name, view_name)

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
