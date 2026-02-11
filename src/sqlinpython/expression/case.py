from __future__ import annotations

from sqlinpython.base import SqlElement
from sqlinpython.expression.core import Expression, Expression13


class CaseExpression(Expression13):
    def __init__(self, prev: ElseClause | ThenClause):
        self._prev = prev

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" END")


class ElseClause(SqlElement):
    def __init__(self, prev: ThenClause, else_: Expression):
        self._prev = prev
        self._else = else_

    @property
    def End(self) -> CaseExpression:
        return CaseExpression(self)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ELSE ")
        self._else._create_query(buffer)


class ThenClause(SqlElement):
    def __init__(self, prev: WhenClause, then: Expression):
        self._prev = prev
        self._then = then

    @property
    def End(self) -> CaseExpression:
        return CaseExpression(self)

    def When(self, when: Expression) -> WhenClause:
        return WhenClause(self, when)

    def Else(self, else_: Expression) -> ElseClause:
        return ElseClause(self, else_)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" THEN ")
        self._then._create_query(buffer)


class WhenClause(SqlElement):
    def __init__(self, prev: SqlElement, when: Expression):
        self._prev = prev
        self._when = when

    def Then(self, then_expr: Expression) -> ThenClause:
        return ThenClause(self, then_expr)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" WHEN ")
        self._when._create_query(buffer)


class CaseWithBaseExpr(SqlElement):
    def __init__(self, prev: CaseKeyword, base: Expression):
        self._prev = prev
        self._base = base

    def When(self, when: Expression) -> WhenClause:
        return WhenClause(self, when)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._base._create_query(buffer)


class CaseKeyword(CaseWithBaseExpr):
    def __init__(self) -> None:
        pass

    def __call__(self, base: Expression) -> CaseWithBaseExpr:
        return CaseWithBaseExpr(self, base)

    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("CASE")


Case = CaseKeyword()
