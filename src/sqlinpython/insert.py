from __future__ import annotations

import typing
from abc import ABC
from typing import override

from typing_extensions import TypeIs

from sqlinpython.base import CompleteSqlQuery, SqlElement, comma_separated
from sqlinpython.expression import (
    AliasedExpression,
    Expression,
    ExpressionOrLiteral,
    Star,
    Star_,
    to_expr,
)
from sqlinpython.indexed_column import IndexedColumn
from sqlinpython.name import Name
from sqlinpython.returning import ReturningBase
from sqlinpython.select_base import SelectStatement, SelectStatement_


def _is_column_names(
    args: tuple[Name | str | SelectStatement, *tuple[Name | str, ...]],
) -> TypeIs[tuple[Name | str, *tuple[Name | str, ...]]]:
    return not isinstance(args[0], SelectStatement_)


# SPEC: https://sqlite.org/lang_insert.html
class InsertStatement(CompleteSqlQuery, ABC):
    pass


class ReturningClause(InsertStatement, ReturningBase):
    pass


class IBeforeReturningClause(InsertStatement, ABC):
    def Returning(
        self, *args: typing.Literal["*"] | Expression | AliasedExpression | Star_
    ) -> ReturningClause:
        values = tuple(Star if arg == "*" else arg for arg in args)
        return ReturningClause(self, values)


class OnConflictUpdateWhere(IBeforeReturningClause):
    def __init__(self, prev: SqlElement, condition: Expression):
        self._prev = prev
        self._condition = condition

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" WHERE ")
        self._condition._create_query(buffer)


_Assignment = tuple[Name | tuple[Name, ...], Expression]


class OnConflictDoUpdateSet(IBeforeReturningClause):
    def __init__(self, prev: SqlElement, assignments: list[_Assignment]) -> None:
        self._prev = prev
        self._assignments = assignments

    def Where(self, condition: ExpressionOrLiteral) -> OnConflictUpdateWhere:
        return OnConflictUpdateWhere(self, to_expr(condition))

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" UPDATE SET ")
        for i, (k, v) in enumerate(self._assignments):
            if i > 0:
                buffer.append(", ")
            if isinstance(k, Name):
                k._create_query(buffer)
                buffer.append(" = ")
            else:
                buffer.append("(")
                comma_separated(buffer, k)
                buffer.append(") = ")
            v._create_query(buffer)


class IBeforeUpsertClause(IBeforeReturningClause, ABC):
    @property
    def OnConflict(self) -> OnConflictClause:
        return OnConflictClause(self)


class OnConflictDoNothing(IBeforeUpsertClause):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" NOTHING")


class OnConflictDo(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Nothing(self) -> OnConflictDoNothing:
        return OnConflictDoNothing(self)

    def UpdateSet(
        self,
        __assignments: dict[str | Name | tuple[str | Name, ...], Expression]
        | None = None,
        /,
        **kwargs: Expression,
    ) -> OnConflictDoUpdateSet:
        assignments: list[_Assignment] = []
        source = __assignments.items() if __assignments is not None else ()
        for k, v in source:
            if isinstance(k, str):
                assignments.append((Name(k), v))
            elif isinstance(k, Name):
                assignments.append((k, v))
            else:
                col_names: list[Name] = []
                for x in k:
                    col_names.append(Name(x) if isinstance(x, str) else x)
                assignments.append((tuple(col_names), v))
        for k, v in kwargs.items():
            assignments.append((Name(k), v))
        if not assignments:
            raise ValueError("UpdateSet() requires at least one assignment")
        return OnConflictDoUpdateSet(self, assignments)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" DO")


class IOnConflictDo(SqlElement, ABC):
    @property
    def Do(self) -> OnConflictDo:
        return OnConflictDo(self)


class OnConflictWhere(IOnConflictDo):
    def __init__(self, prev: SqlElement, expr: Expression):
        self._prev = prev
        self._expr = expr

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" WHERE ")
        self._expr._create_query(buffer)


class OnConflictCall(IOnConflictDo):
    def __init__(self, prev: SqlElement, args: tuple[IndexedColumn, ...]):
        self._prev = prev
        self._args = args

    def Where(self, expr: ExpressionOrLiteral) -> OnConflictWhere:
        return OnConflictWhere(self, to_expr(expr))

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append("(")
        comma_separated(buffer, self._args)
        buffer.append(")")


class OnConflictClause(IOnConflictDo):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def __call__(self, *args: IndexedColumn) -> OnConflictCall:
        return OnConflictCall(self, args)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ON CONFLICT")


class InsertDefaultValues(IBeforeReturningClause):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" DEFAULT VALUES")


class InsertSelect(IBeforeUpsertClause):
    def __init__(self, prev: SqlElement, select_stm: SelectStatement) -> None:
        self._prev = prev
        self._select_stm = select_stm

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._select_stm._create_query(buffer)


class InsertValues(IBeforeUpsertClause):
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
            comma_separated(buffer, tuple)
            buffer.append(")")


class IInsertBody(SqlElement, ABC):
    def Values(self, *values: tuple[ExpressionOrLiteral, ...]) -> InsertValues:
        return InsertValues(
            self, tuple(tuple(to_expr(e) for e in row) for row in values)
        )

    def __call__(self, select_stm: SelectStatement, /) -> InsertSelect:
        return InsertSelect(self, select_stm)

    @property
    def DefaultValues(self) -> InsertDefaultValues:
        return InsertDefaultValues(self)


class InsertColumnNames(IInsertBody):
    def __init__(self, prev: SqlElement, column_names: tuple[Name, ...]) -> None:
        self._prev = prev
        self._column_names = column_names

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" (")
        comma_separated(buffer, self._column_names)
        buffer.append(")")


class ICallableWithColumnNames(IInsertBody, ABC):
    @typing.overload
    def __call__(self, select_stm: SelectStatement, /) -> InsertSelect: ...  # ty: ignore[invalid-overload]  # https://github.com/astral-sh/ty/issues/1746

    @typing.overload
    def __call__(
        self, *column_names: *tuple[Name | str, *tuple[Name | str, ...]]
    ) -> InsertColumnNames: ...

    @override
    def __call__(
        self,
        *column_names: *tuple[Name | str | SelectStatement, *tuple[Name | str, ...]],
    ) -> InsertColumnNames | InsertSelect:
        if _is_column_names(column_names):
            names = tuple(
                Name(name) if isinstance(name, str) else name for name in column_names
            )
            return InsertColumnNames(self, names)
        first = column_names[0]
        assert isinstance(first, SelectStatement_)
        return InsertSelect(self, first)


class InsertNameAs(ICallableWithColumnNames):
    def __init__(self, prev: SqlElement, alias: Name) -> None:
        self._prev = prev
        self._alias = alias

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" AS ")
        self._alias._create_query(buffer)


class IntoName(ICallableWithColumnNames):
    def __init__(self, prev: SqlElement, schema: Name, table: Name | None) -> None:
        self._prev = prev
        self._schema = schema
        self._table = table

    def As(self, alias: Name | str) -> InsertNameAs:
        if isinstance(alias, str):
            alias = Name(alias)
        return InsertNameAs(self, alias)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._schema._create_query(buffer)
        if self._table is not None:
            buffer.append(".")
            self._table._create_query(buffer)


class Into_(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def __call__(
        self, schema: Name | str, table: Name | str | None = None, /
    ) -> IntoName:
        if isinstance(schema, str):
            schema = Name(schema)
        if isinstance(table, str):
            table = Name(table)
        return IntoName(self, schema, table)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" INTO")


class InsertOr(SqlElement):
    def __init__(
        self,
        prev: SqlElement,
        conflict: typing.Literal["ABORT", "FAIL", "IGNORE", "REPLACE", "ROLLBACK"],
    ) -> None:
        self._prev = prev
        self._conflict = conflict

    @property
    def Into(self) -> Into_:
        return Into_(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" OR {self._conflict}")


class InsertKeyword(SqlElement):
    def __init__(self, prev: SqlElement | None = None) -> None:
        self._prev = prev

    @property
    def Into(self) -> Into_:
        return Into_(self)

    @property
    def OrAbort(self) -> InsertOr:
        return InsertOr(self, "ABORT")

    @property
    def OrFail(self) -> InsertOr:
        return InsertOr(self, "FAIL")

    @property
    def OrIgnore(self) -> InsertOr:
        return InsertOr(self, "IGNORE")

    @property
    def OrReplace(self) -> InsertOr:
        return InsertOr(self, "REPLACE")

    @property
    def OrRollback(self) -> InsertOr:
        return InsertOr(self, "ROLLBACK")

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
