from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, override

from sqlinpython.base import SqlElement, comma_separated
from sqlinpython.insert import InsertKeyword, ReplaceKeyword
from sqlinpython.name import Name
from sqlinpython.select_base import Complete, SelectStatement

if TYPE_CHECKING:
    from sqlinpython.delete import DeleteKeyword
    from sqlinpython.select import SelectKeyword, ValuesKeyword
    from sqlinpython.update import UpdateKeyword


# SPEC: https://sqlite.org/syntax/common-table-expression.html
class CommonTableExpression(SqlElement, ABC):
    pass


class CteWithSelectStmt(CommonTableExpression):
    def __init__(self, prev: SqlElement, select_stmt: SelectStatement) -> None:
        self._prev = prev
        self._select_stmt = select_stmt

    @override
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

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" MATERIALIZED")


class CteNot_(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Materialized(self) -> Materialized_:
        return Materialized_(self)

    @override
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

    @override
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

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append("(")
        comma_separated(buffer, self._column_names)
        buffer.append(")")


# TODO: Integrate TableName into expression module
class TableName(Name, CteTableNameWithColumns):
    def __call__(
        self, column_name: Name | str, *more_column_names: Name | str
    ) -> CteTableNameWithColumns:
        all_names = (column_name,) + more_column_names
        names = tuple(Name(n) if isinstance(n, str) else n for n in all_names)
        return CteTableNameWithColumns(self, names)


# SPEC: https://sqlite.org/lang_insert.html (WITH clause portion)
class WithClause(SqlElement):
    def __init__(
        self, prev: SqlElement, ctes: tuple[CommonTableExpression, ...]
    ) -> None:
        self._prev = prev
        self._ctes = ctes

    @property
    def Delete(self) -> DeleteKeyword:
        from sqlinpython.delete import DeleteKeyword

        return DeleteKeyword(self)

    @property
    def Update(self) -> UpdateKeyword:
        from sqlinpython.update import UpdateKeyword

        return UpdateKeyword(self)

    @property
    def Replace(self) -> ReplaceKeyword:
        return ReplaceKeyword(self)

    @property
    def Insert(self) -> InsertKeyword:
        return InsertKeyword(self)

    @property
    def Select(self) -> SelectKeyword[Complete]:
        from sqlinpython.select import SelectKeyword

        return SelectKeyword(self)

    @property
    def Values(self) -> ValuesKeyword[Complete]:
        from sqlinpython.select import ValuesKeyword

        return ValuesKeyword(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        comma_separated(buffer, self._ctes)


class WithRecursive(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def __call__(
        self, *ctes: *tuple[CommonTableExpression, *tuple[CommonTableExpression, ...]]
    ) -> WithClause:
        return WithClause(self, ctes)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" RECURSIVE")


class WithKeyword(WithRecursive):
    def __init__(self) -> None:
        pass

    @property
    def Recursive(self) -> WithRecursive:
        return WithRecursive(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("WITH")


With = WithKeyword()
