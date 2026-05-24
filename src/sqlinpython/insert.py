from __future__ import annotations

import typing
from abc import ABC
from typing import override

from typing_extensions import TypeIs

from sqlinpython.base import CompleteSqlQuery, SqlElement, comma_separated
from sqlinpython.column_name import ColumnName
from sqlinpython.expression import Expression, Star
from sqlinpython.expression.core import AliasedExpression
from sqlinpython.expression.function import Star_
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
        comma_separated(buffer, self._args)
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


class BeforeUpsertClause(IBeforeReturningClause, ABC):
    @property
    def OnConflict(self) -> OnConflictClause:
        return OnConflictClause(self)


class OnConflictUpdateWhere(IBeforeReturningClause):
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
            if isinstance(k, ColumnName):
                k._create_query(buffer)
                buffer.append(" = ")
            else:
                buffer.append("(")
                comma_separated(buffer, k)
                buffer.append(") = ")
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
            comma_separated(buffer, tuple)
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


class InsertDefaultValues(IBeforeReturningClause):
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
        comma_separated(buffer, self._column_names)
        buffer.append(")")


class InsertNameAs(InsertColumnNames):
    def __init__(self, prev: SqlElement, alias: Name) -> None:
        self._prev = prev
        self._alias = alias

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

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" AS ")
        self._alias._create_query(buffer)


class IntoName(InsertNameAs):
    def __init__(self, prev: SqlElement, schema: Name, table: Name | None) -> None:
        self._prev = prev
        self._schema = schema
        self._table = table

    # TODO: Is alias a name or is it more restrictive?
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
