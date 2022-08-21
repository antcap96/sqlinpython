from __future__ import annotations

from typing import Literal

from sqlinpython.base import SqlElement
from sqlinpython.column_def import ColumnDef
from sqlinpython.expression import Expression
from sqlinpython.name import Name
from sqlinpython.reference import SqlRef


class TableSpecWithJoin(SqlElement):
    def Join(self, other: TableSpec, on: Expression) -> TableSpecWithJoin:
        return TableSpecWithJoin(self, other, "", on)

    def InnerJoin(self, other: TableSpec, on: Expression) -> TableSpecWithJoin:
        return TableSpecWithJoin(self, other, "INNER", on)

    def LeftJoin(self, other: TableSpec, on: Expression) -> TableSpecWithJoin:
        return TableSpecWithJoin(self, other, "LEFT", on)

    def LeftOuterJoin(self, other: TableSpec, on: Expression) -> TableSpecWithJoin:
        return TableSpecWithJoin(self, other, "LEFT OUTER", on)

    def RightJoin(self, other: TableSpec, on: Expression) -> TableSpecWithJoin:
        return TableSpecWithJoin(self, other, "RIGHT", on)

    def RightOuterJoin(self, other: TableSpec, on: Expression) -> TableSpecWithJoin:
        return TableSpecWithJoin(self, other, "RIGHT OUTER", on)

    def __init__(
        self,
        prev: SqlElement,
        with_: TableSpecWithJoin,
        how: Literal["", "INNER", "LEFT", "LEFT OUTER", "RIGHT", "RIGHT OUTER"],
        on: Expression,
    ) -> None:
        self._prev = prev
        self._with = with_
        self._how = how
        self._on = on

    def _create_query(self) -> str:
        join = self._how + " JOIN" if self._how else "JOIN"
        return (
            f"{self._prev._create_query()} {join} {self._with._create_query()}"
            f" ON {self._on._create_query()}"
        )


class TableSpec(TableSpecWithJoin):
    pass


class AliasedTableRef(TableSpec):
    pass


class TableRefWithTableSample(AliasedTableRef):
    def __init__(self, prev: SqlElement, fraction: float):
        self._prev = prev
        self._fraction = fraction

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} TABLESAMPLE({self._fraction})"


class TableRefWithColumnDef(TableRefWithTableSample):
    def __init__(self, prev: SqlElement, column_defs: tuple[ColumnDef, ...]) -> None:
        self._prev = prev
        self._column_defs = column_defs

    def _create_query(self) -> str:
        column_defs = ", ".join(col._create_query() for col in self._column_defs)
        return f"{self._prev._create_query()}({column_defs})"

    def TableSample(self, fraction: float) -> TableRefWithTableSample:
        return TableRefWithTableSample(self, fraction)


class TableRefWithAlias(TableRefWithColumnDef):
    def __init__(self, prev: SqlElement, alias: Name, explicit_as: bool):
        self._prev = prev
        self._alias = alias
        self._explicit_as = explicit_as

    def _create_query(self) -> str:
        as_ = ""
        if self._explicit_as:
            as_ = "AS "
        return f"{self._prev._create_query()} {as_}{self._alias._create_query()}"

    def __call__(self, *column_defs: ColumnDef) -> TableRefWithColumnDef:
        return TableRefWithColumnDef(self, column_defs)


class TableRef(SqlRef, TableRefWithAlias):
    def As(self, alias: Name | str, explicit_as: bool = True) -> TableRefWithAlias:
        if isinstance(alias, str):
            alias = Name(alias)

        return TableRefWithAlias(self, alias, explicit_as)
