from __future__ import annotations

import re
from typing import Literal

from sqlinpython.base import SqlElement

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


class ColumnNameWithRowTimestamp(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} ROW_TIMESTAMP"


class ColumnNameWithAscDesc(ColumnNameWithRowTimestamp):
    def __init__(self, prev: SqlElement, kind: Literal["ASC", "DESC"]) -> None:
        self._prev = prev
        self._kind = kind

    @property
    def RowTimestamp(self) -> ColumnNameWithRowTimestamp:
        return ColumnNameWithRowTimestamp(self)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._kind}"


class ColumnName(Name, ColumnNameWithAscDesc):
    @property
    def Asc(self) -> ColumnNameWithAscDesc:
        return ColumnNameWithAscDesc(self, "ASC")

    @property
    def Desc(self) -> ColumnNameWithAscDesc:
        return ColumnNameWithAscDesc(self, "DESC")
