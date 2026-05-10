from __future__ import annotations

import typing
from abc import ABC
from typing import Literal, override

from sqlinpython.base import CompleteSqlQuery, SqlElement, comma_separated
from sqlinpython.expression import Expression, Star
from sqlinpython.expression.core import AliasedExpression
from sqlinpython.expression.function import Star_
from sqlinpython.name import Name
from sqlinpython.returning import ReturningBase
from sqlinpython.table_or_subquery import TableOrSubquery

# SPEC: https://sqlite.org/lang_update.html
# SPEC: https://sqlite.org/syntax/qualified-table-name.html

# NOTE: The qualified-table-name classes (UpdateTable, UpdateTableAliased,
# UpdateTableIndexedBy, UpdateTableNotIndexed) duplicate those in delete.py.
# A unified QualifiedTableName_[T] with self-typed Where/Set would be ideal,
# but QTN must be CompleteSqlQuery for DELETE (bare DELETE FROM table is valid)
# while it must not be for UPDATE (SET is required).


class UpdateStatement(CompleteSqlQuery, ABC):
    pass


class UpdateReturning(UpdateStatement, ReturningBase):
    pass


class IBeforeReturningClause(UpdateStatement, ABC):
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
            if isinstance(k, tuple):
                buffer.append("(")
                for j, col in enumerate(k):
                    if j > 0:
                        buffer.append(", ")
                    col._create_query(buffer)
                buffer.append(") = ")
            else:
                k._create_query(buffer)
                buffer.append(" = ")
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
            if isinstance(k, tuple):
                col_names: list[Name] = []
                for x in k:
                    if isinstance(x, str):
                        col_names.append(Name(x))
                    elif isinstance(x, Name):
                        col_names.append(x)
                assignments.append((tuple(col_names), v))
            elif isinstance(k, str):
                assignments.append((Name(k), v))
            else:
                assignments.append((k, v))
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
    def __init__(self, prev: SqlElement, schema: Name | None, name: Name) -> None:
        self._prev = prev
        self._schema = schema
        self._name = name

    def As(self, alias: Name | str) -> UpdateTableAliased:
        if isinstance(alias, str):
            alias = Name(alias)
        return UpdateTableAliased(self, alias)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        if self._schema is not None:
            self._schema._create_query(buffer)
            buffer.append(".")
        self._name._create_query(buffer)


class UpdateOr(SqlElement):
    def __init__(
        self,
        prev: SqlElement,
        conflict: Literal["ABORT", "FAIL", "IGNORE", "REPLACE", "ROLLBACK"],
    ) -> None:
        self._prev = prev
        self._conflict = conflict

    def __call__(
        self, schema_or_name: Name | str, name: Name | str | None = None, /
    ) -> UpdateTable:
        if isinstance(schema_or_name, str):
            schema_or_name = Name(schema_or_name)
        if isinstance(name, str):
            name = Name(name)
        if name is None:
            return UpdateTable(self, None, schema_or_name)
        return UpdateTable(self, schema_or_name, name)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" OR {self._conflict}")


class UpdateKeyword(SqlElement):
    def __init__(self, prev: SqlElement | None = None) -> None:
        self._prev = prev

    def __call__(
        self, schema_or_name: Name | str, name: Name | str | None = None, /
    ) -> UpdateTable:
        if isinstance(schema_or_name, str):
            schema_or_name = Name(schema_or_name)
        if isinstance(name, str):
            name = Name(name)
        if name is None:
            return UpdateTable(self, None, schema_or_name)
        return UpdateTable(self, schema_or_name, name)

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

# TODO: update-stmt-limited (https://sqlite.org/syntax/update-stmt-limited.html)
# adds ORDER BY and LIMIT/OFFSET support and is not yet implemented.
