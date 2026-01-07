from __future__ import annotations

from abc import ABCMeta

from sqlinpython.base import SqlElement
from sqlinpython.expression import Expression, Term, TermBeforeBracket


class CaseWhenOperations(SqlElement, metaclass=ABCMeta):
    def When(self, expression: Expression) -> CaseQueryWithWhen:
        return CaseQueryWithWhen(self, expression)


class CaseQuery(TermBeforeBracket):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} END"


class CaseQueryWithElse(SqlElement):
    def __init__(self, prev: SqlElement, expression: Expression) -> None:
        self._prev = prev
        self._expression = expression

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} ELSE {self._expression._create_query()}"

    @property
    def End(self) -> CaseQuery:
        return CaseQuery(self)


class CaseQueryWithThen(CaseQueryWithElse, CaseWhenOperations):
    def __init__(self, prev: SqlElement, term: Term) -> None:
        self._prev = prev
        self._term = term

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} THEN {self._term._create_query()}"

    def Else(self, expression: Expression) -> CaseQueryWithElse:
        return CaseQueryWithElse(self, expression)


class CaseQueryWithWhen(SqlElement):
    def __init__(self, prev: SqlElement, expression: Expression) -> None:
        self._prev = prev
        self._expression = expression

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} WHEN {self._expression._create_query()}"

    def Then(self, term: Term) -> CaseQueryWithThen:
        return CaseQueryWithThen(self, term)


class CaseQueryWithTerm(CaseWhenOperations):
    def __init__(self, prev: SqlElement, term: Term) -> None:
        self._prev = prev
        self._term = term

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._term._create_query()}"


class CaseKeyword(CaseWhenOperations):
    def __call__(self, term: Term) -> CaseQueryWithTerm:
        return CaseQueryWithTerm(self, term)

    def _create_query(self) -> str:
        return "CASE"


Case = CaseKeyword()
