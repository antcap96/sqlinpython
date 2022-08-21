from __future__ import annotations

from abc import ABCMeta

from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.datatype import DataType
from sqlinpython.expression import Operand, Term
from sqlinpython.reference import SqlRef


class ColumnRef(SqlRef, Term):
    def __call__(self, data_type: DataType) -> ColumnDefWithDataType:
        return ColumnDefWithDataType(self, data_type)


class ColumnDef(CompleteSqlQuery, metaclass=ABCMeta):
    pass


class ColumnDefWithRowTimestamp(ColumnDef):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} ROW_TIMESTAMP"


class ColumnDefWithAscDesc(ColumnDefWithRowTimestamp):
    def __init__(self, prev: SqlElement, ascending: bool) -> None:
        self._prev = prev
        self._ascending = ascending

    @property
    def RowTimestamp(self) -> ColumnDefWithRowTimestamp:
        return ColumnDefWithRowTimestamp(self)

    def _create_query(self) -> str:
        if self._ascending:
            suffix = "ASC"
        else:
            suffix = "DESC"
        return f"{self._prev._create_query()} {suffix}"


class ColumnDefWithPrimaryKey(ColumnDefWithAscDesc):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Asc(self) -> ColumnDefWithAscDesc:
        return ColumnDefWithAscDesc(self, True)

    @property
    def Desc(self) -> ColumnDefWithAscDesc:
        return ColumnDefWithAscDesc(self, False)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} PRIMARY KEY"


class ColumnDefWithDefault(ColumnDef):
    def __init__(self, prev: SqlElement, operand: Operand) -> None:
        self._prev = prev
        self._operand = operand

    @property
    def PrimaryKey(self) -> ColumnDefWithPrimaryKey:
        return ColumnDefWithPrimaryKey(self)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} DEFAULT {self._operand._create_query()}"


class ColumnDefWithNull(ColumnDefWithDefault):
    def __init__(self, prev: SqlElement, is_null: bool) -> None:
        self._prev = prev
        self._is_null = is_null

    def Default(self, operand: Operand) -> ColumnDefWithDefault:
        return ColumnDefWithDefault(self, operand)

    def _create_query(self) -> str:
        if self._is_null:
            suffix = "NULL"
        else:
            suffix = "NOT NULL"
        return f"{self._prev._create_query()} {suffix}"


class ColumnDefWithDataType(ColumnDefWithNull):
    def __init__(self, prev: SqlElement, data_type: DataType) -> None:
        self._prev = prev
        self._data_type = data_type

    @property
    def NotNull(self) -> ColumnDefWithNull:
        return ColumnDefWithNull(self, False)

    @property
    def Null(self) -> ColumnDefWithNull:
        return ColumnDefWithNull(self, True)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._data_type._create_query()}"
