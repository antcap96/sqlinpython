from __future__ import annotations

from sqlinpython.base import NotImplementedSqlElement, SqlElement
from sqlinpython.name import Name


class SelectStatement(NotImplementedSqlElement):
    def __init__(self) -> None:
        super().__init__("<select-stmt>")


# SPEC: https://sqlite.org/syntax/common-table-expression.html
class CommonTableExpression(SqlElement):
    pass


class CteWithSelectStmt(CommonTableExpression):
    def __init__(self, prev: SqlElement, select_stmt: SelectStatement) -> None:
        self._prev = prev
        self._select_stmt = select_stmt

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" (")
        self._select_stmt._create_query(buffer)
        buffer.append(")")


class Materialized_(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def __call__(self, select_stmt: SelectStatement) -> CteWithSelectStmt:
        return CteWithSelectStmt(self, select_stmt)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" MATERIALIZED")


class CteNot_(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Materialized(self) -> Materialized_:
        return Materialized_(self)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" NOT")


class As_(Materialized_):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Not(self) -> CteNot_:
        return CteNot_(self)

    @property
    def Materialized(self) -> Materialized_:
        return Materialized_(self)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" AS")


class CteTableNameWithColumns(SqlElement):
    def __init__(self, prev: SqlElement, column_names: tuple[Name, ...]) -> None:
        self._prev = prev
        self._column_names = column_names

    @property
    def As(self) -> As_:
        return As_(self)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append("(")
        for i, column_name in enumerate(self._column_names):
            if i > 0:
                buffer.append(", ")
            column_name._create_query(buffer)
        buffer.append(")")


# TODO: Integrate TableName into expression module
class TableName(Name, CteTableNameWithColumns):
    def __call__(
        self, column_name: Name | str, *more_column_names: Name | str
    ) -> CteTableNameWithColumns:
        all_names = (column_name,) + more_column_names
        names = tuple(Name(n) if isinstance(n, str) else n for n in all_names)
        return CteTableNameWithColumns(self, names)
