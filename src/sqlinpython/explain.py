from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import CompleteSqlQuery, NonExplainSqlQuery, SqlElement

# SPEC: https://sqlite.org/syntax/sql-stmt.html


class ExplainStatement(CompleteSqlQuery, ABC):
    pass


class ExplainStatementWithQuery(ExplainStatement):
    def __init__(self, prev: SqlElement, stmt: NonExplainSqlQuery) -> None:
        self._prev = prev
        self._stmt = stmt

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._stmt._create_query(buffer)


class IExplainCall(SqlElement, ABC):
    def __call__(self, stmt: NonExplainSqlQuery) -> ExplainStatementWithQuery:
        return ExplainStatementWithQuery(self, stmt)


class ExplainQueryPlanKeyword(IExplainCall):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" QUERY PLAN")


class ExplainKeyword(IExplainCall):
    def __init__(self) -> None:
        pass

    @property
    def QueryPlan(self) -> ExplainQueryPlanKeyword:
        return ExplainQueryPlanKeyword(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("EXPLAIN")


Explain = ExplainKeyword()
