from __future__ import annotations

import typing
from abc import ABC
from typing import override

from sqlinpython.base import CompleteSqlQuery, SqlElement, comma_separated
from sqlinpython.expression import Expression, Star
from sqlinpython.expression.core import AliasedExpression
from sqlinpython.expression.function import Star_
from sqlinpython.name import Name
from sqlinpython.ordering_term import OrderingTerm
from sqlinpython.returning import ReturningBase

# SPEC: https://sqlite.org/lang_delete.html
# SPEC: https://sqlite.org/syntax/qualified-table-name.html
# SPEC: https://sqlite.org/syntax/delete-stmt-limited.html

# NOTE: The qualified-table-name classes (DeleteFrom, DeleteFromAliased,
# DeleteFromIndexedBy, DeleteFromNotIndexed) will be duplicated in update.py.
# A unified QualifiedTableName_[T] with self-typed Where/Set would be ideal,
# but QTN must be CompleteSqlQuery for DELETE (bare DELETE FROM table is valid)
# while it must not be for UPDATE (SET is required).


class DeleteStatementLimited(CompleteSqlQuery, ABC):
    """Base for delete-stmt-limited (ORDER BY / LIMIT requires SQLITE_ENABLE_UPDATE_DELETE_LIMIT)."""

    pass


class DeleteStatement(DeleteStatementLimited, ABC):
    """Base for delete-stmt (no ORDER BY / LIMIT; no compile-time flag needed)."""

    pass


# ---------------------------------------------------------------------------
# LIMIT / OFFSET (delete-stmt-limited)
# ---------------------------------------------------------------------------


class DeleteLimitOffset(DeleteStatementLimited):
    def __init__(self, prev: SqlElement, offset: Expression) -> None:
        self._prev = prev
        self._offset = offset

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" OFFSET ")
        self._offset._create_query(buffer)


class DeleteLimitComma(DeleteStatementLimited):
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


class DeleteLimit(DeleteStatementLimited):
    def __init__(self, prev: SqlElement, limit: Expression) -> None:
        self._prev = prev
        self._limit = limit

    def Offset(self, offset: Expression) -> DeleteLimitOffset:
        return DeleteLimitOffset(self, offset)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" LIMIT ")
        self._limit._create_query(buffer)


class IDeleteLimit(SqlElement, ABC):
    @typing.overload
    def Limit(self, expr: Expression) -> DeleteLimit: ...
    @typing.overload
    def Limit(self, expr: Expression, offset: Expression) -> DeleteLimitComma: ...
    def Limit(
        self, expr: Expression, offset: Expression | None = None
    ) -> DeleteLimit | DeleteLimitComma:
        if offset is None:
            return DeleteLimit(self, expr)
        return DeleteLimitComma(self, expr, offset)


class DeleteOrderBy(DeleteStatementLimited, IDeleteLimit):
    def __init__(self, prev: SqlElement, terms: tuple[OrderingTerm, ...]) -> None:
        self._prev = prev
        self._terms = terms

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ORDER BY ")
        comma_separated(buffer, self._terms)


class IDeleteOrderBy(IDeleteLimit, ABC):
    def OrderBy(
        self, *terms: *tuple[OrderingTerm, *tuple[OrderingTerm, ...]]
    ) -> DeleteOrderBy:
        return DeleteOrderBy(self, terms)


# ---------------------------------------------------------------------------
# Regular delete-stmt chain
# ---------------------------------------------------------------------------


class DeleteReturning(DeleteStatement, IDeleteOrderBy, ReturningBase):
    pass


class IBeforeReturningClause(DeleteStatement, IDeleteOrderBy, ABC):
    def Returning(
        self,
        *args: typing.Literal["*"] | Expression | AliasedExpression | Star_,
    ) -> DeleteReturning:
        values = tuple(Star if arg == "*" else arg for arg in args)
        return DeleteReturning(self, values)


class DeleteWhere(IBeforeReturningClause):
    def __init__(self, prev: SqlElement, condition: Expression) -> None:
        self._prev = prev
        self._condition = condition

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" WHERE ")
        self._condition._create_query(buffer)


class IBeforeWhereClause(IBeforeReturningClause, ABC):
    def Where(self, condition: Expression) -> DeleteWhere:
        return DeleteWhere(self, condition)


class DeleteFromNotIndexed(IBeforeWhereClause):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" NOT INDEXED")


class DeleteFromIndexedBy(IBeforeWhereClause):
    def __init__(self, prev: SqlElement, index_name: Name) -> None:
        self._prev = prev
        self._index_name = index_name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" INDEXED BY ")
        self._index_name._create_query(buffer)


class IIndexHints(IBeforeWhereClause, ABC):
    def IndexedBy(self, index_name: Name | str) -> DeleteFromIndexedBy:
        if isinstance(index_name, str):
            index_name = Name(index_name)
        return DeleteFromIndexedBy(self, index_name)

    @property
    def NotIndexed(self) -> DeleteFromNotIndexed:
        return DeleteFromNotIndexed(self)


class DeleteFromAliased(IIndexHints):
    def __init__(self, prev: SqlElement, alias: Name) -> None:
        self._prev = prev
        self._alias = alias

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" AS ")
        self._alias._create_query(buffer)


class DeleteFrom(IIndexHints):
    def __init__(self, prev: SqlElement, schema: Name | None, name: Name) -> None:
        self._prev = prev
        self._schema = schema
        self._name = name

    def As(self, alias: Name | str) -> DeleteFromAliased:
        if isinstance(alias, str):
            alias = Name(alias)
        return DeleteFromAliased(self, alias)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        if self._schema is not None:
            self._schema._create_query(buffer)
            buffer.append(".")
        self._name._create_query(buffer)


class DeleteKeyword(SqlElement):
    def __init__(self, prev: SqlElement | None = None) -> None:
        self._prev = prev

    def From(
        self, schema_or_name: Name | str, name: Name | str | None = None, /
    ) -> DeleteFrom:
        if isinstance(schema_or_name, str):
            schema_or_name = Name(schema_or_name)
        if isinstance(name, str):
            name = Name(name)
        if name is None:
            return DeleteFrom(self, None, schema_or_name)
        return DeleteFrom(self, schema_or_name, name)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        if self._prev is None:
            buffer.append("DELETE FROM")
        else:
            self._prev._create_query(buffer)
            buffer.append(" DELETE FROM")


Delete = DeleteKeyword()
