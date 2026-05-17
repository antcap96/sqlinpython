from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.name import Name


# SPEC: https://sqlite.org/lang_reindex.html
class ReindexStatement(CompleteSqlQuery, ABC):
    pass


class ReindexSchemaComplete(ReindexStatement):
    def __init__(self, prev: SqlElement, schema: Name, table_or_index: Name) -> None:
        self._prev = prev
        self._schema = schema
        self._table_or_index = table_or_index

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._schema._create_query(buffer)
        buffer.append(".")
        self._table_or_index._create_query(buffer)


class ReindexExpressions(ReindexStatement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" EXPRESSIONS")


class ReindexWithName(ReindexStatement):
    def __init__(self, prev: SqlElement, name: Name) -> None:
        self._prev = prev
        self._name = name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._name._create_query(buffer)


class ReindexKeyword(ReindexStatement):
    def __call__(self, name: Name | str) -> ReindexWithName:
        if isinstance(name, str):
            name = Name(name)
        return ReindexWithName(self, name)

    def Schema(
        self, schema: Name | str, table_or_index: Name | str
    ) -> ReindexSchemaComplete:
        if isinstance(schema, str):
            schema = Name(schema)
        if isinstance(table_or_index, str):
            table_or_index = Name(table_or_index)
        return ReindexSchemaComplete(self, schema, table_or_index)

    @property
    def Expressions(self) -> ReindexExpressions:
        return ReindexExpressions(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("REINDEX")


Reindex = ReindexKeyword()
