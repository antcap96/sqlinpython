from __future__ import annotations

from sqlinpython.base import SqlElement
from sqlinpython.name import ColumnNameWithRowTimestamp, Name


class ConstrainName(Name):
    pass


class ConstrainKeyword(SqlElement):
    def __call__(self, constrain_name: ConstrainName) -> ConstrainWithName:
        return ConstrainWithName(self, constrain_name)

    def _create_query(self) -> str:
        return "CONSTRAINT"


class ConstrainWithName(SqlElement):
    def __init__(self, prev: SqlElement, constrain_name: ConstrainName) -> None:
        self._prev = prev
        self._constrain_name = constrain_name

    @property
    def PrimaryKey(self) -> ConstrainWithPrimaryKey:
        return ConstrainWithPrimaryKey(self)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._constrain_name._create_query()}"


class ConstrainWithPrimaryKey(SqlElement):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} PRIMARY KEY"

    def __call__(
        self,
        first_column_name: ColumnNameWithRowTimestamp,
        /,
        *column_names: ColumnNameWithRowTimestamp,
    ) -> ConstrainType:
        return ConstrainType(self, (first_column_name, *column_names))


class ConstrainType(SqlElement):
    def __init__(
        self,
        prev: SqlElement,
        column_names: tuple[ColumnNameWithRowTimestamp, ...],
    ) -> None:
        self._prev = prev
        self._column_names = column_names

    def _create_query(self) -> str:
        col_name_queries = [col_name._create_query() for col_name in self._column_names]
        col_name_query = ", ".join(col_name_queries)
        return f"{self._prev._create_query()}({col_name_query})"


Constrain = ConstrainKeyword()
