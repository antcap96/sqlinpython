from __future__ import annotations

import re
from typing import Optional

from sqlinpython.base import CompleteSqlQuery, SqlElement

UNQUOTED_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def quote_if_necessary(s: str, force_quote: bool = False) -> str:
    result = re.match(UNQUOTED_NAME_PATTERN, s)

    if force_quote or result is None:
        s = s.replace('"', '""')
        s = f'"{s}"'

    return s


class Name(SqlElement):
    def __init__(self, name: str, force_quote: bool = False) -> None:
        name = quote_if_necessary(name, force_quote)
        self._name = name

    def _create_query(self) -> str:
        return self._name


class ColumnName(Name):
    pass


class ConstrainName(Name):
    pass


class ColumnNameConstrainWithRowTimestamp(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} ROW_TIMESTAMP"


class ColumnNameConstrainWithAscDesc(ColumnNameConstrainWithRowTimestamp):
    def __init__(self, prev: SqlElement, asc: Optional[bool]) -> None:
        self._prev = prev
        self._asc = asc

    @property
    def RowTimestamp(self) -> ColumnNameConstrainWithRowTimestamp:
        return ColumnNameConstrainWithRowTimestamp(self)

    def _create_query(self) -> str:
        suffix = ""
        match self._asc:
            case True:
                suffix = " ASC"
            case False:
                suffix = " DESC"
            case None:
                suffix = ""
        return f"{self._prev._create_query()}{suffix}"


class ColumnNameConstrain(ColumnNameConstrainWithAscDesc):
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def Asc(self) -> ColumnNameConstrainWithAscDesc:
        return ColumnNameConstrainWithAscDesc(self, True)

    @property
    def Desc(self) -> ColumnNameConstrainWithAscDesc:
        return ColumnNameConstrainWithAscDesc(self, False)

    def _create_query(self) -> str:
        return self._name


Column = ColumnNameConstrain

# TODO: move Constrain to a diferent file
class Constrain(SqlElement):
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
        return f"{self._prev._create_query()} {self._constrain_name._name}"


class ConstrainWithPrimaryKey(SqlElement):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} PRIMARY KEY"

    def __call__(
        self,
        first_column_name: ColumnNameConstrainWithRowTimestamp,
        /,
        *column_names: ColumnNameConstrainWithRowTimestamp,
    ) -> ConstrainQuery:
        return ConstrainQuery(self, (first_column_name, *column_names))


class ConstrainQuery(CompleteSqlQuery):
    def __init__(
        self,
        prev: SqlElement,
        column_names: tuple[ColumnNameConstrainWithRowTimestamp, ...],
    ) -> None:
        self._prev = prev
        self._column_names = column_names

    def _create_query(self) -> str:
        col_name_queries = [col_name._create_query() for col_name in self._column_names]
        col_name_query = ", ".join(col_name_queries)
        return f"{self._prev._create_query()}({col_name_query})"


constrain = Constrain()
