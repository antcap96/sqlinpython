from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import SqlElement, comma_separated
from sqlinpython.expression import (
    AliasedExpression,
    Expression,
    ExpressionOrLiteral,
    Star,
    Star_,
    to_expr,
)

# RETURNING result-columns: "*" sentinel, expressions, aliased expressions, or bare
# literals (via to_expr). RETURNING does not support table-name.* so there is no
# TableStarResultColumn here.
ReturningColumnArg = ExpressionOrLiteral | AliasedExpression | Star_


def resolve_returning_column(
    arg: ReturningColumnArg,
) -> Star_ | Expression | AliasedExpression:
    # The isinstance guard matters: Expression.__eq__ builds a (truthy)
    # EqExpression instead of returning False.
    if isinstance(arg, str) and arg == "*":
        return Star
    if isinstance(arg, (Expression, AliasedExpression, Star_)):
        return arg
    return to_expr(arg)


class ReturningBase(SqlElement, ABC):
    def __init__(
        self,
        prev: SqlElement,
        values: tuple[Star_ | Expression | AliasedExpression, ...],
    ) -> None:
        self._prev = prev
        self._values = values

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" RETURNING ")
        comma_separated(buffer, self._values)
