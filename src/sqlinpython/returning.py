from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import SqlElement, comma_separated
from sqlinpython.expression import AliasedExpression, Expression, Star_


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
