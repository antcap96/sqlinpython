from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import SqlElement
from sqlinpython.expression.core import Expression, Expression13
from sqlinpython.expression.literal import ExpressionOrLiteral, to_expr


class CaseExpression(Expression13):
    def __init__(self, prev: ElseClause | ThenClause):
        self._prev = prev

    @override
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

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ELSE ")
        self._else._create_query(buffer)


class IWhenCallable(SqlElement, ABC):
    def When(self, when: ExpressionOrLiteral) -> WhenClause:
        return WhenClause(self, to_expr(when))


class ThenClause(IWhenCallable):
    def __init__(self, prev: WhenClause, then: Expression):
        self._prev = prev
        self._then = then

    @property
    def End(self) -> CaseExpression:
        return CaseExpression(self)

    def Else(self, else_: ExpressionOrLiteral) -> ElseClause:
        return ElseClause(self, to_expr(else_))

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" THEN ")
        self._then._create_query(buffer)


class WhenClause(SqlElement):
    def __init__(self, prev: SqlElement, when: Expression):
        self._prev = prev
        self._when = when

    def Then(self, then_expr: ExpressionOrLiteral) -> ThenClause:
        return ThenClause(self, to_expr(then_expr))

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" WHEN ")
        self._when._create_query(buffer)


class CaseWithBaseExpr(IWhenCallable):
    def __init__(self, prev: CaseKeyword, base: Expression):
        self._prev = prev
        self._base = base

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._base._create_query(buffer)


class CaseKeyword(IWhenCallable):
    def __init__(self) -> None:
        pass

    def __call__(self, base: ExpressionOrLiteral) -> CaseWithBaseExpr:
        return CaseWithBaseExpr(self, to_expr(base))

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("CASE")


Case = CaseKeyword()
