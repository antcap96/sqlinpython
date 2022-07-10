from __future__ import annotations
from typing import Optional, Union
from sqlinpython.base import SqlElement, CompleteSqlQuery, NotImplementedSqlElement
from sqlinpython.value import Value
from sqlinpython.name import ConstrainQuery
from sqlinpython.reference import TableRef
from sqlinpython.column_def import ColumnDef


class TableOption(NotImplementedSqlElement):
    pass


class bindParameter(SqlElement):
    pass


class bindParameterIndex(bindParameter):
    def __init__(self, i: int) -> None:
        self.i = i

    def _create_query(self) -> str:
        return f":{self.i}"


class bindParameterQ(bindParameter):
    def _create_query(self) -> str:
        return "?"


class bindParam:
    @staticmethod
    def index(i: int) -> bindParameterIndex:
        return bindParameterIndex(i)

    q = bindParameterQ()


SplitPoint = Union[Value, bindParameter]


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
        constrain: Optional[ConstrainQuery],
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
        constrain: Optional[ConstrainQuery] = None,
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


class CreateTable(CreateTableIfNotExists):
    def __init__(self) -> None:
        pass

    @property
    def ifNotExists(self) -> CreateTableIfNotExists:
        return CreateTableIfNotExists(self)

    def _create_query(self) -> str:
        return "CREATE TABLE"


createTable = CreateTable()
