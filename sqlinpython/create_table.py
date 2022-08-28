from __future__ import annotations

from abc import ABCMeta
from typing import Optional, Union

from sqlinpython.base import CompleteSqlQuery, NotImplementedSqlElement, SqlElement
from sqlinpython.column_def import ColumnDef
from sqlinpython.expression import Value
from sqlinpython.name import ConstrainType
from sqlinpython.table_spec import TableRef


class TableOption(NotImplementedSqlElement):
    pass


class BindParameter(SqlElement, metaclass=ABCMeta):
    pass


class BindParameterIndex(BindParameter):
    def __init__(self, i: int) -> None:
        self._i = i

    def _create_query(self) -> str:
        return f":{self._i}"


class BindParameterQ(BindParameter):
    def _create_query(self) -> str:
        return "?"


class BindParam:
    @staticmethod
    def Index(i: int) -> BindParameterIndex:
        return BindParameterIndex(i)

    q = BindParameterQ()


SplitPoint = Union[Value, BindParameter]


class CreateTableWithSplitOn(CompleteSqlQuery):
    def __init__(self, prev: SqlElement, split_points: tuple[SplitPoint, ...]) -> None:
        self._prev = prev
        self._split_points = split_points

    def _create_query(self) -> str:
        split_points = ", ".join(
            split_point._create_query() for split_point in self._split_points
        )
        return f"{self._prev._create_query()} SPLIT ON({split_points})"


class CreateTableWithOptions(CreateTableWithSplitOn):
    def __init__(
        self, prev: SqlElement, table_options: tuple[TableOption, ...]
    ) -> None:
        self._prev = prev
        self._table_options = table_options

    def SplitOn(
        self, first_split_point: SplitPoint, *split_points: SplitPoint
    ) -> CreateTableWithSplitOn:
        return CreateTableWithSplitOn(self, (first_split_point, *split_points))

    def _create_query(self) -> str:
        table_options = ", ".join(
            option._create_query() for option in self._table_options
        )
        return f"{self._prev._create_query()} {table_options}"


class CreateTableWithColumnDef(CreateTableWithOptions):
    def __init__(
        self,
        prev: SqlElement,
        column_defs: tuple[ColumnDef, ...],
        constrain: Optional[ConstrainType],
    ) -> None:
        self._prev = prev
        self._column_defs = column_defs
        self._constrain = constrain

    def __call__(self, *table_options: TableOption) -> CreateTableWithOptions:
        return CreateTableWithOptions(self, table_options)

    def _create_query(self) -> str:
        column_definitions = ", ".join(
            definition._create_query() for definition in self._column_defs
        )
        constrain = ""
        if self._constrain is not None:
            constrain = " " + self._constrain._create_query()

        return f"{self._prev._create_query()} ({column_definitions}{constrain})"


class CreateTableWithRef(SqlElement):
    def __init__(self, prev: SqlElement, table_ref: TableRef) -> None:
        self._prev = prev
        self._table_ref = table_ref

    def __call__(
        self,
        first_column_def: ColumnDef,
        /,
        *column_defs: ColumnDef,
        constrain: Optional[ConstrainType] = None,
    ) -> CreateTableWithColumnDef:
        return CreateTableWithColumnDef(
            self, (first_column_def, *column_defs), constrain
        )

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._table_ref._create_query()}"


class CreateTableIfNotExists(SqlElement):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    # TODO consider passing the arguments of TableRef directly here
    def __call__(self, table_ref: TableRef) -> CreateTableWithRef:
        return CreateTableWithRef(self, table_ref)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} IF NOT EXISTS"


class CreateTableKeyword(CreateTableIfNotExists):
    def __init__(self) -> None:
        pass

    @property
    def IfNotExists(self) -> CreateTableIfNotExists:
        return CreateTableIfNotExists(self)

    def _create_query(self) -> str:
        return "CREATE TABLE"


CreateTable = CreateTableKeyword()
