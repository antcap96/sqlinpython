from __future__ import annotations

import typing
from abc import ABC
from typing import override

from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.expression import Expression, Star
from sqlinpython.expression.core import AliasedExpression
from sqlinpython.expression.function import Star_
from sqlinpython.name import Name
from sqlinpython.returning import ReturningBase

# SPEC: https://sqlite.org/lang_delete.html
# SPEC: https://sqlite.org/syntax/qualified-table-name.html

# NOTE: The qualified-table-name classes (DeleteFrom, DeleteFromAliased,
# DeleteFromIndexedBy, DeleteFromNotIndexed) will be duplicated in update.py.
# A unified QualifiedTableName_[T] with self-typed Where/Set would be ideal,
# but QTN must be CompleteSqlQuery for DELETE (bare DELETE FROM table is valid)
# while it must not be for UPDATE (SET is required).


class DeleteStatement(CompleteSqlQuery, ABC):
    pass


class DeleteReturning(DeleteStatement, ReturningBase):
    pass


class IBeforeReturningClause(DeleteStatement, ABC):
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
