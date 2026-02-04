from __future__ import annotations

from typing import Literal

from sqlinpython.base import SqlElement
from sqlinpython.column_definition import ColumnNameWithType
from sqlinpython.name import Name
from sqlinpython.table_constraint import TableConstraint


class ForeignKeyClause(ColumnNameWithType, TableConstraint):
    pass


class InitiallyHow(ForeignKeyClause):
    def __init__(self, prev: SqlElement, how: Literal["IMMEDIATE", "DEFERRED"]) -> None:
        self._prev = prev
        self._how = how

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._how}")


class Initially_(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Deferred(self) -> InitiallyHow:
        return InitiallyHow(self, "DEFERRED")

    @property
    def Immediate(self) -> InitiallyHow:
        return InitiallyHow(self, "IMMEDIATE")

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" INITIALLY")


class Deferrable_(ForeignKeyClause):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Initially(self) -> Initially_:
        return Initially_(self)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" DEFERRABLE")


class Not_(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Deferrable(self) -> Deferrable_:
        return Deferrable_(self)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" NOT")


class BeforeDeferrable(ForeignKeyClause):
    @property
    def On(self) -> On_:
        return On_(self)

    def Match(self, name: Name | str) -> Match_:
        if isinstance(name, str):
            name = Name(name)
        return Match_(self, name)

    @property
    def Not(self) -> Not_:
        return Not_(self)

    @property
    def Deferrable(self) -> Deferrable_:
        return Deferrable_(self)


class Match_(BeforeDeferrable):
    def __init__(self, prev: BeforeDeferrable, name: Name) -> None:
        self._prev = prev
        self._name = name

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" MATCH ")
        self._name._create_query(buffer)


class OnActionDo(BeforeDeferrable):
    def __init__(
        self,
        prev: SqlElement,
        action: Literal["SET NULL", "SET DEFAULT", "CASCADE", "RESTRICT", "NO ACTION"],
    ) -> None:
        self._prev = prev
        self._action = action

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._action}")


class OnAction(SqlElement):
    def __init__(self, prev: SqlElement, action: Literal["DELETE", "UPDATE"]) -> None:
        self._prev = prev
        self._action = action

    @property
    def SetNull(self) -> OnActionDo:
        return OnActionDo(self, "SET NULL")

    @property
    def SetDefault(self) -> OnActionDo:
        return OnActionDo(self, "SET DEFAULT")

    @property
    def Cascade(self) -> OnActionDo:
        return OnActionDo(self, "CASCADE")

    @property
    def Restrict(self) -> OnActionDo:
        return OnActionDo(self, "RESTRICT")

    @property
    def NoAction(self) -> OnActionDo:
        return OnActionDo(self, "NO ACTION")

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._action}")


class On_(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Delete(self) -> OnAction:
        return OnAction(self, "DELETE")

    @property
    def Update(self) -> OnAction:
        return OnAction(self, "UPDATE")

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ON")


class ReferenceWithColumns(BeforeDeferrable):
    def __init__(self, prev: SqlElement, column_names: tuple[Name, ...]) -> None:
        self._prev = prev
        self._column_names = column_names

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" (")
        for i, column_name in enumerate(self._column_names):
            if i > 0:
                buffer.append(", ")
            column_name._create_query(buffer)
        buffer.append(")")


class References_(ReferenceWithColumns):
    def __init__(self, prev: SqlElement, table_name: str | Name) -> None:
        if isinstance(table_name, str):
            table_name = Name(table_name)
        self._prev = prev
        self._table_name = table_name

    def __call__(self, *column_names: Name | str) -> ReferenceWithColumns:
        names = tuple(
            Name(column_name) if isinstance(column_name, str) else column_name
            for column_name in column_names
        )
        return ReferenceWithColumns(self, names)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" REFERENCES ")
        self._table_name._create_query(buffer)
