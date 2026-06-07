from __future__ import annotations

from typing import overload

from sqlinpython.expression.core import (
    Expression12,
    SchemaTableColumnName,
    TableColumnName,
)
from sqlinpython.name import Name


class ColumnName(Name, Expression12):
    """Expression atom referring to a column. Use ColumnDef for column definitions."""


@overload
def col(__schema: str, __table: str, __column: str) -> SchemaTableColumnName: ...
@overload
def col(__table: str, __column: str) -> TableColumnName: ...
@overload
def col(__column: str) -> ColumnName: ...
def col(
    n1: str, n2: str | None = None, n3: str | None = None, /
) -> SchemaTableColumnName | TableColumnName | ColumnName:
    if n2 is None:
        return ColumnName(n1)
    if n3 is None:
        return TableColumnName(n1, n2)
    return SchemaTableColumnName(n1, n2, n3)
