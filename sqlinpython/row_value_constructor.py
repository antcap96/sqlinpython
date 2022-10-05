from sqlinpython.base import SqlElement
from sqlinpython.expression import Expression


class RowValueConstructor(SqlElement):
    def __init__(self, e1: Expression, e2: Expression, /, *es: Expression) -> None:
        expressions = (e1, e2, *es)
        self._expressions = expressions

    def _create_query(self) -> str:
        expressions = ", ".join(e._create_query() for e in self._expressions)
        return f"({expressions})"
