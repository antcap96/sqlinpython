from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import SqlElement
from sqlinpython.expression import Expression
from sqlinpython.expression.core import AliasedExpression
from sqlinpython.expression.function import Star_


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
        for i, val in enumerate(self._values):
            if i > 0:
                buffer.append(", ")
            val._create_query(buffer)
