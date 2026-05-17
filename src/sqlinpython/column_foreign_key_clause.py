from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import SqlElement
from sqlinpython.column_definition import IColumnConstraint
from sqlinpython.name import Name

# SPEC: https://sqlite.org/syntax/foreign-key-clause.html


class ColumnForeignKeyClause(IColumnConstraint, ABC):
    pass


class IColumnBeforeDeferrable(SqlElement, ABC):
    @property
    def On(self) -> ColumnOn_:
        return ColumnOn_(self)

    def Match(self, name: Name | str) -> ColumnMatch_:
        if isinstance(name, str):
            name = Name(name)
        return ColumnMatch_(self, name)

    @property
    def Not(self) -> ColumnNot_:
        return ColumnNot_(self)

    @property
    def Deferrable(self) -> ColumnDeferrable_:
        return ColumnDeferrable_(self)


class ColumnBeforeDeferrable(ColumnForeignKeyClause, IColumnBeforeDeferrable, ABC):
    pass


class ColumnOn_(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Delete(self) -> ColumnOnAction_:
        return ColumnOnAction_(self, "DELETE")

    @property
    def Update(self) -> ColumnOnAction_:
        return ColumnOnAction_(self, "UPDATE")

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ON")


class ColumnOnAction_(SqlElement):
    def __init__(self, prev: SqlElement, event: str) -> None:
        self._prev = prev
        self._event = event

    @property
    def SetNull(self) -> ColumnOnActionDo:
        return ColumnOnActionDo(self, "SET NULL")

    @property
    def SetDefault(self) -> ColumnOnActionDo:
        return ColumnOnActionDo(self, "SET DEFAULT")

    @property
    def Cascade(self) -> ColumnOnActionDo:
        return ColumnOnActionDo(self, "CASCADE")

    @property
    def Restrict(self) -> ColumnOnActionDo:
        return ColumnOnActionDo(self, "RESTRICT")

    @property
    def NoAction(self) -> ColumnOnActionDo:
        return ColumnOnActionDo(self, "NO ACTION")

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._event}")


class ColumnOnActionDo(ColumnBeforeDeferrable):
    def __init__(self, prev: SqlElement, action: str) -> None:
        self._prev = prev
        self._action = action

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._action}")


class ColumnMatch_(ColumnBeforeDeferrable):
    def __init__(self, prev: SqlElement, name: Name) -> None:
        self._prev = prev
        self._name = name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" MATCH ")
        self._name._create_query(buffer)


class ColumnNot_(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Deferrable(self) -> ColumnDeferrable_:
        return ColumnDeferrable_(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" NOT")


class ColumnDeferrable_(ColumnForeignKeyClause):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Initially(self) -> ColumnInitially_:
        return ColumnInitially_(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" DEFERRABLE")


class ColumnInitially_(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Deferred(self) -> ColumnInitiallyHow:
        return ColumnInitiallyHow(self, "DEFERRED")

    @property
    def Immediate(self) -> ColumnInitiallyHow:
        return ColumnInitiallyHow(self, "IMMEDIATE")

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" INITIALLY")


class ColumnInitiallyHow(ColumnForeignKeyClause):
    def __init__(self, prev: SqlElement, how: str) -> None:
        self._prev = prev
        self._how = how

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._how}")


class ColumnReferenceWithColumns(ColumnBeforeDeferrable):
    def __init__(self, prev: SqlElement, column_names: tuple[Name, ...]) -> None:
        self._prev = prev
        self._column_names = column_names

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" (")
        for i, column_name in enumerate(self._column_names):
            if i > 0:
                buffer.append(", ")
            column_name._create_query(buffer)
        buffer.append(")")


class ColumnReferences_(ColumnBeforeDeferrable):
    def __init__(self, prev: SqlElement, table_name: Name) -> None:
        self._prev = prev
        self._table_name = table_name

    def __call__(self, *column_names: Name | str) -> ColumnReferenceWithColumns:
        names = tuple(Name(c) if isinstance(c, str) else c for c in column_names)
        return ColumnReferenceWithColumns(self, names)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" REFERENCES ")
        self._table_name._create_query(buffer)
