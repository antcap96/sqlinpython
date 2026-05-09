from __future__ import annotations

from typing import override

from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.name import Name


# SPEC: https://sqlite.org/lang_analyze.html
class AnalyzeComplete(CompleteSqlQuery):
    def __init__(self, prev: SqlElement, schema: Name, table: Name | None) -> None:
        self._prev = prev
        self._schema = schema
        self._table = table

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._schema._create_query(buffer)
        if self._table is not None:
            buffer.append(".")
            self._table._create_query(buffer)


class AnalyzeKeyword(CompleteSqlQuery):
    def __init__(self) -> None:
        pass

    def __call__(
        self,
        schema: Name | str,
        table: Name | str | None = None,
        /,
    ) -> AnalyzeComplete:
        if isinstance(schema, str):
            schema = Name(schema)
        if isinstance(table, str):
            table = Name(table)
        return AnalyzeComplete(self, schema, table)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("ANALYZE")


Analyze = AnalyzeKeyword()
