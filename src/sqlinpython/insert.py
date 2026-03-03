from __future__ import annotations

import typing
from typing import override
from abc import ABC

from sqlinpython.column_name import ColumnName
from sqlinpython.base import CompleteSqlQuery, NotImplementedSqlElement, SqlElement
from sqlinpython.expression import Expression, Star
from sqlinpython.expression.core import AliasedExpression
from sqlinpython.expression.function import Star_
from sqlinpython.indexed_column import IndexedColumn
from sqlinpython.name import Name


class SelectStatement(NotImplementedSqlElement):
    def __init__(self) -> None:
        super().__init__("<select-stmt>")


# SPEC: https://sqlite.org/lang_insert.html
class InsertStatement(CompleteSqlQuery, ABC):
    pass


class ReturningClause(InsertStatement):
    def __init__(
        self,
        prev: SqlElement,
        values: tuple[Star_ | Expression | AliasedExpression, ...],
    ):
        self._prev = prev
        self._values = values

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" RETURNING ")
        for i, val in enumerate(self._values):
            if i > 0:
                buffer.append(", ")
            val._create_query(buffer)


class BeforeReturningClause(InsertStatement, ABC):
    def Returning(
        self, *args: typing.Literal["*"] | Expression | AliasedExpression | Star_
    ) -> ReturningClause:
        args = tuple(Star if arg == "*" else arg for arg in args)
        return ReturningClause(self, args)


class OnConflictWhere(SqlElement):
    def __init__(self, prev: SqlElement, expr: Expression):
        self._prev = prev
        self._expr = expr

    @property
    def Do(self) -> OnConflictDo:
        return OnConflictDo(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" WHERE ")
        self._expr._create_query(buffer)


class OnConflictCall(OnConflictWhere):
    def __init__(self, prev: SqlElement, args: tuple[IndexedColumn, ...]):
        self._prev = prev
        self._args = args

    def Where(self, expr: Expression) -> OnConflictWhere:
        return OnConflictWhere(self, expr)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append("(")
        for i, arg in enumerate(self._args):
            if i > 0:
                buffer.append(", ")
            arg._create_query(buffer)
        buffer.append(")")


class OnConflictClause(OnConflictCall):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def __call__(self, *args: IndexedColumn) -> OnConflictCall:
        return OnConflictCall(self, args)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ON CONFLICT")


class BeforeUpsertClause(BeforeReturningClause, ABC):
    @property
    def OnConflict(self) -> OnConflictClause:
        return OnConflictClause(self)


class OnConflictUpdateWhere(BeforeReturningClause):
    def __init__(self, prev: SqlElement, condition: Expression):
        self._prev = prev
        self._condition = condition

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" WHERE ")
        self._condition._create_query(buffer)


class OnConflictDoUpdateSet(OnConflictUpdateWhere):
    def __init__(
        self,
        prev: SqlElement,
        args: list[tuple[tuple[ColumnName, ...] | ColumnName, Expression]],
    ) -> None:
        self._prev = prev
        self._args = args

    def Where(self, condition: Expression) -> OnConflictUpdateWhere:
        return OnConflictUpdateWhere(self, condition)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" UPDATE SET ")
        for i, (k, v) in enumerate(self._args):
            if i > 0:
                buffer.append(", ")
            if isinstance(k, tuple):
                buffer.append("(")
                for j, x in enumerate(k):
                    if j > 0:
                        buffer.append(", ")
                    x._create_query(buffer)
                buffer.append(") = ")
            else:
                k._create_query(buffer)
                buffer.append(" = ")
            v._create_query(buffer)


class OnConflictDo(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Nothing(self) -> OnConflictDoNothing:
        return OnConflictDoNothing(self)

    def UpdateSet(
        self, *args: tuple[tuple[ColumnName | str, ...] | ColumnName | str, Expression]
    ) -> OnConflictDoUpdateSet:
        arguments: list[tuple[tuple[ColumnName, ...] | ColumnName, Expression]] = []
        for k, v in args:
            match k:
                case ColumnName():
                    arguments.append((k, v))
                case str():
                    arguments.append((ColumnName(k), v))
                case _:
                    key = tuple(
                        x if isinstance(x, ColumnName) else ColumnName(x) for x in k
                    )
                    arguments.append((key, v))
        return OnConflictDoUpdateSet(self, arguments)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" DO")


class OnConflictDoNothing(BeforeUpsertClause):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" NOTHING")


class InsertValues(BeforeUpsertClause):
    def __init__(
        self, prev: SqlElement, values: tuple[tuple[Expression, ...], ...]
    ) -> None:
        self._prev = prev
        self._values = values

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" VALUES ")
        for i, tuple in enumerate(self._values):
            if i > 0:
                buffer.append(", ")
            buffer.append("(")
            for j, value in enumerate(tuple):
                if j > 0:
                    buffer.append(", ")
                value._create_query(buffer)
            buffer.append(")")


class InsertSelect(BeforeUpsertClause):
    def __init__(self, prev: SqlElement, select_stm: SelectStatement) -> None:
        self._prev = prev
        self._select_stm = select_stm

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._select_stm._create_query(buffer)


class InsertDefaultValues(BeforeReturningClause):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" DEFAULT VALUES")


class InsertColumnNames(SqlElement):
    def __init__(self, prev: SqlElement, column_names: tuple[Name, ...]) -> None:
        self._prev = prev
        self._column_names = column_names

    def Values(self, *values: tuple[Expression, ...]) -> InsertValues:
        return InsertValues(self, values)

    def __call__(self, select_stm: SelectStatement, /) -> InsertSelect:
        return InsertSelect(self, select_stm)

    @property
    def DefaultValues(self) -> InsertDefaultValues:
        return InsertDefaultValues(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" (")
        for i, column_name in enumerate(self._column_names):
            if i > 0:
                buffer.append(", ")
            column_name._create_query(buffer)
        buffer.append(")")


class InsertNameAs(InsertColumnNames):
    def __init__(self, prev: SqlElement, alias: Name) -> None:
        self._prev = prev
        self._alias = alias

    @typing.overload
    def __call__(self, select_stm: SelectStatement, /) -> InsertSelect: ...

    @typing.overload
    def __call__(
        self, first_column_name: Name | str, /, *column_names: Name | str
    ) -> InsertColumnNames: ...

    @override
    def __call__(
        self,
        first_column_name: Name | str | SelectStatement,
        /,
        *column_names: Name | str,
    ) -> InsertColumnNames | InsertSelect:
        if isinstance(first_column_name, SelectStatement):
            return InsertSelect(self, first_column_name)
        if isinstance(first_column_name, str):
            first_column_name = Name(first_column_name)
        column_names = tuple(
            Name(name) if isinstance(name, str) else name for name in column_names
        )
        return InsertColumnNames(self, (first_column_name, *column_names))

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" AS ")
        self._alias._create_query(buffer)


class IntoName(InsertNameAs):
    def __init__(self, prev: SqlElement, name: Name, name2: Name | None) -> None:
        self._prev = prev
        self._name = name
        self._name2 = name2

    # TODO: Is alias a name or is it more restrictive?
    def As(self, alias: Name | str) -> InsertNameAs:
        if isinstance(alias, str):
            alias = Name(alias)
        return InsertNameAs(self, alias)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._name._create_query(buffer)
        if self._name2 is not None:
            buffer.append(".")
            self._name2._create_query(buffer)


class Into_(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def __call__(self, name: Name | str, name2: Name | str | None = None) -> IntoName:
        if isinstance(name, str):
            name = Name(name)
        if isinstance(name2, str):
            name2 = Name(name2)
        return IntoName(self, name, name2)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" INTO")


class InsertAfterOr(SqlElement):
    def __init__(
        self,
        prev: SqlElement,
        value: typing.Literal["ABORT", "FAIL", "IGNORE", "REPLACE", "ROLLBACK"],
    ) -> None:
        self._prev = prev
        self._value = value

    @property
    def Into(self) -> Into_:
        return Into_(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._value}")


class InsertOr(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Abort(self) -> InsertAfterOr:
        return InsertAfterOr(self, "ABORT")

    @property
    def Fail(self) -> InsertAfterOr:
        return InsertAfterOr(self, "FAIL")

    @property
    def Ignore(self) -> InsertAfterOr:
        return InsertAfterOr(self, "IGNORE")

    @property
    def Replace(self) -> InsertAfterOr:
        return InsertAfterOr(self, "REPLACE")

    @property
    def Rollback(self) -> InsertAfterOr:
        return InsertAfterOr(self, "ROLLBACK")

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" OR")


class InsertKeyword(SqlElement):
    def __init__(self, prev: SqlElement | None = None) -> None:
        self._prev = prev

    @property
    def Into(self) -> Into_:
        return Into_(self)

    @property
    def Or(self) -> InsertOr:
        return InsertOr(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        if self._prev is None:
            buffer.append("INSERT")
        else:
            self._prev._create_query(buffer)
            buffer.append(" INSERT")


class ReplaceKeyword(SqlElement):
    def __init__(self, prev: SqlElement | None = None) -> None:
        self._prev = prev

    @property
    def Into(self) -> Into_:
        return Into_(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        if self._prev is None:
            buffer.append("REPLACE")
        else:
            self._prev._create_query(buffer)
            buffer.append(" REPLACE")


# Entry point singletons
Insert = InsertKeyword()
Replace = ReplaceKeyword()
