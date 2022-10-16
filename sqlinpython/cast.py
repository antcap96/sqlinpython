from __future__ import annotations

from sqlinpython.datatype import DataType
from sqlinpython.expression import Expression, Term


class Cast(Term):
    def __init__(self, expression: Expression, _as: DataType) -> None:
        self._expression = expression
        self._as = _as

    def _create_query(self) -> str:
        return (
            f"CAST ({self._expression._create_query()} AS {self._as._create_query()})"
        )
