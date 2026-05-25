from __future__ import annotations

import typing
from abc import ABC
from typing import Literal, override

from sqlinpython.base import CompleteSqlQuery, SqlElement, comma_separated
from sqlinpython.expression import Expression, Star
from sqlinpython.expression.core import AliasedExpression
from sqlinpython.expression.function import Star_
from sqlinpython.name import Name
from sqlinpython.ordering_term import OrderingTerm
from sqlinpython.returning import ReturningBase
from sqlinpython.table_or_subquery import TableOrSubquery

# SPEC: https://sqlite.org/lang_update.html
# SPEC: https://sqlite.org/syntax/qualified-table-name.html
# SPEC: https://sqlite.org/syntax/update-stmt-limited.html

# NOTE: The qualified-table-name classes (UpdateTable, UpdateTableAliased,
# UpdateTableIndexedBy, UpdateTableNotIndexed) duplicate those in delete.py.
# A unified QualifiedTableName_[T] with self-typed Where/Set would be ideal,
# but QTN must be CompleteSqlQuery for DELETE (bare DELETE FROM table is valid)
# while it must not be for UPDATE (SET is required).


class UpdateStatementLimited(CompleteSqlQuery, ABC):
    """Base for update-stmt-limited (ORDER BY / LIMIT requires SQLITE_ENABLE_UPDATE_DELETE_LIMIT)."""

    pass


class UpdateStatement(UpdateStatementLimited, ABC):
    """Base for update-stmt (no ORDER BY / LIMIT; no compile-time flag needed)."""

    pass


# ---------------------------------------------------------------------------
# LIMIT / OFFSET (update-stmt-limited)
# ---------------------------------------------------------------------------


class UpdateLimitOffset(UpdateStatementLimited):
    def __init__(self, prev: SqlElement, offset: Expression) -> None:
        self._prev = prev
        self._offset = offset

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" OFFSET ")
        self._offset._create_query(buffer)


class UpdateLimitComma(UpdateStatementLimited):
    def __init__(self, prev: SqlElement, limit: Expression, offset: Expression) -> None:
        self._prev = prev
        self._limit = limit
        self._offset = offset

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" LIMIT ")
        self._limit._create_query(buffer)
        buffer.append(", ")
        self._offset._create_query(buffer)


class UpdateLimit(UpdateStatementLimited):
    def __init__(self, prev: SqlElement, limit: Expression) -> None:
        self._prev = prev
        self._limit = limit

    def Offset(self, offset: Expression) -> UpdateLimitOffset:
        return UpdateLimitOffset(self, offset)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" LIMIT ")
        self._limit._create_query(buffer)


class IUpdateLimit(SqlElement, ABC):
    @typing.overload
    def Limit(self, expr: Expression) -> UpdateLimit: ...
    @typing.overload
    def Limit(self, expr: Expression, offset: Expression) -> UpdateLimitComma: ...
    def Limit(
        self, expr: Expression, offset: Expression | None = None
    ) -> UpdateLimit | UpdateLimitComma:
        if offset is None:
            return UpdateLimit(self, expr)
        return UpdateLimitComma(self, expr, offset)


class UpdateOrderBy(UpdateStatementLimited, IUpdateLimit):
    def __init__(self, prev: SqlElement, terms: tuple[OrderingTerm, ...]) -> None:
        self._prev = prev
        self._terms = terms

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ORDER BY ")
        comma_separated(buffer, self._terms)


class IUpdateOrderBy(IUpdateLimit, ABC):
    def OrderBy(
        self, *terms: *tuple[OrderingTerm, *tuple[OrderingTerm, ...]]
    ) -> UpdateOrderBy:
        return UpdateOrderBy(self, terms)


# ---------------------------------------------------------------------------
# Regular update-stmt chain
# ---------------------------------------------------------------------------


class UpdateReturning(UpdateStatement, IUpdateOrderBy, ReturningBase):
    pass


class IBeforeReturningClause(UpdateStatement, IUpdateOrderBy, ABC):
    def Returning(
        self,
        *args: typing.Literal["*"] | Expression | AliasedExpression | Star_,
    ) -> UpdateReturning:
        values = tuple(Star if arg == "*" else arg for arg in args)
        return UpdateReturning(self, values)


class UpdateWhere(IBeforeReturningClause):
    def __init__(self, prev: SqlElement, condition: Expression) -> None:
        self._prev = prev
        self._condition = condition

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" WHERE ")
        self._condition._create_query(buffer)


class IBeforeWhereClause(IBeforeReturningClause, ABC):
    def Where(self, condition: Expression) -> UpdateWhere:
        return UpdateWhere(self, condition)


class UpdateSetFrom(IBeforeWhereClause):
    def __init__(self, prev: SqlElement, sources: tuple[TableOrSubquery, ...]) -> None:
        self._prev = prev
        self._sources = sources

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" FROM ")
        comma_separated(buffer, self._sources)


_Assignment = tuple[Name | tuple[Name, ...], Expression]


class UpdateSet(IBeforeWhereClause):
    def __init__(self, prev: SqlElement, assignments: list[_Assignment]) -> None:
        self._prev = prev
        self._assignments = assignments

    def From(self, source: TableOrSubquery, *more: TableOrSubquery) -> UpdateSetFrom:
        return UpdateSetFrom(self, (source,) + more)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" SET ")
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


class IBeforeSetClause(SqlElement, ABC):
    def Set(
        self,
        __assignments: dict[str | Name | tuple[str | Name, ...], Expression]
        | None = None,
        /,
        **kwargs: Expression,
    ) -> UpdateSet:
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
            raise ValueError("Set() requires at least one assignment")
        return UpdateSet(self, assignments)


class UpdateTableNotIndexed(IBeforeSetClause):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" NOT INDEXED")


class UpdateTableIndexedBy(IBeforeSetClause):
    def __init__(self, prev: SqlElement, index_name: Name) -> None:
        self._prev = prev
        self._index_name = index_name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" INDEXED BY ")
        self._index_name._create_query(buffer)


class IIndexHints(IBeforeSetClause, ABC):
    def IndexedBy(self, index_name: Name | str) -> UpdateTableIndexedBy:
        if isinstance(index_name, str):
            index_name = Name(index_name)
        return UpdateTableIndexedBy(self, index_name)

    @property
    def NotIndexed(self) -> UpdateTableNotIndexed:
        return UpdateTableNotIndexed(self)


class UpdateTableAliased(IIndexHints):
    def __init__(self, prev: SqlElement, alias: Name) -> None:
        self._prev = prev
        self._alias = alias

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" AS ")
        self._alias._create_query(buffer)


class UpdateTable(IIndexHints):
    def __init__(self, prev: SqlElement, schema: Name, table: Name | None) -> None:
        self._prev = prev
        self._schema = schema
        self._table = table

    def As(self, alias: Name | str) -> UpdateTableAliased:
        if isinstance(alias, str):
            alias = Name(alias)
        return UpdateTableAliased(self, alias)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._schema._create_query(buffer)
        if self._table is not None:
            buffer.append(".")
            self._table._create_query(buffer)


class UpdateOr(SqlElement):
    def __init__(
        self,
        prev: SqlElement,
        conflict: Literal["ABORT", "FAIL", "IGNORE", "REPLACE", "ROLLBACK"],
    ) -> None:
        self._prev = prev
        self._conflict = conflict

    def __call__(
        self, schema: Name | str, name: Name | str | None = None, /
    ) -> UpdateTable:
        if isinstance(schema, str):
            schema = Name(schema)
        if isinstance(name, str):
            name = Name(name)
        return UpdateTable(self, schema, name)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" OR {self._conflict}")


class UpdateKeyword(SqlElement):
    def __init__(self, prev: SqlElement | None = None) -> None:
        self._prev = prev

    def __call__(
        self, schema: Name | str, name: Name | str | None = None, /
    ) -> UpdateTable:
        if isinstance(schema, str):
            schema = Name(schema)
        if isinstance(name, str):
            name = Name(name)
        return UpdateTable(self, schema, name)

    @property
    def OrAbort(self) -> UpdateOr:
        return UpdateOr(self, "ABORT")

    @property
    def OrFail(self) -> UpdateOr:
        return UpdateOr(self, "FAIL")

    @property
    def OrIgnore(self) -> UpdateOr:
        return UpdateOr(self, "IGNORE")

    @property
    def OrReplace(self) -> UpdateOr:
        return UpdateOr(self, "REPLACE")

    @property
    def OrRollback(self) -> UpdateOr:
        return UpdateOr(self, "ROLLBACK")

    @override
    def _create_query(self, buffer: list[str]) -> None:
        if self._prev is None:
            buffer.append("UPDATE")
        else:
            self._prev._create_query(buffer)
            buffer.append(" UPDATE")


Update = UpdateKeyword()
