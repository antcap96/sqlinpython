from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import SqlElement
from sqlinpython.name import Name
from sqlinpython.table_constraint import TableConstraint

# SPEC: https://sqlite.org/syntax/foreign-key-clause.html


class TableForeignKeyClause(TableConstraint, ABC):
    pass


class ITableBeforeDeferrable(SqlElement, ABC):
    @property
    def On(self) -> TableOn_:
        return TableOn_(self)

    def Match(self, name: Name | str) -> TableMatch_:
        if isinstance(name, str):
            name = Name(name)
        return TableMatch_(self, name)

    @property
    def Not(self) -> TableNot_:
        return TableNot_(self)

    @property
    def Deferrable(self) -> TableDeferrable_:
        return TableDeferrable_(self)


class TableBeforeDeferrable(TableForeignKeyClause, ITableBeforeDeferrable, ABC):
    pass


class TableOn_(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Delete(self) -> TableOnAction_:
        return TableOnAction_(self, "DELETE")

    @property
    def Update(self) -> TableOnAction_:
        return TableOnAction_(self, "UPDATE")

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ON")


class TableOnAction_(SqlElement):
    def __init__(self, prev: SqlElement, event: str) -> None:
        self._prev = prev
        self._event = event

    @property
    def SetNull(self) -> TableOnActionDo:
        return TableOnActionDo(self, "SET NULL")

    @property
    def SetDefault(self) -> TableOnActionDo:
        return TableOnActionDo(self, "SET DEFAULT")

    @property
    def Cascade(self) -> TableOnActionDo:
        return TableOnActionDo(self, "CASCADE")

    @property
    def Restrict(self) -> TableOnActionDo:
        return TableOnActionDo(self, "RESTRICT")

    @property
    def NoAction(self) -> TableOnActionDo:
        return TableOnActionDo(self, "NO ACTION")

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._event}")


class TableOnActionDo(TableBeforeDeferrable):
    def __init__(self, prev: SqlElement, action: str) -> None:
        self._prev = prev
        self._action = action

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._action}")


class TableMatch_(TableBeforeDeferrable):
    def __init__(self, prev: SqlElement, name: Name) -> None:
        self._prev = prev
        self._name = name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" MATCH ")
        self._name._create_query(buffer)


class TableNot_(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Deferrable(self) -> TableDeferrable_:
        return TableDeferrable_(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" NOT")


class TableDeferrable_(TableForeignKeyClause):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Initially(self) -> TableInitially_:
        return TableInitially_(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" DEFERRABLE")


class TableInitially_(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Deferred(self) -> TableInitiallyHow:
        return TableInitiallyHow(self, "DEFERRED")

    @property
    def Immediate(self) -> TableInitiallyHow:
        return TableInitiallyHow(self, "IMMEDIATE")

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" INITIALLY")


class TableInitiallyHow(TableForeignKeyClause):
    def __init__(self, prev: SqlElement, how: str) -> None:
        self._prev = prev
        self._how = how

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._how}")


class TableReferenceWithColumns(TableBeforeDeferrable):
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


class TableReferences_(TableBeforeDeferrable):
    def __init__(self, prev: SqlElement, table_name: Name) -> None:
        self._prev = prev
        self._table_name = table_name

    def __call__(self, *column_names: Name | str) -> TableReferenceWithColumns:
        names = tuple(Name(c) if isinstance(c, str) else c for c in column_names)
        return TableReferenceWithColumns(self, names)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" REFERENCES ")
        self._table_name._create_query(buffer)
