from sqlinpython.base import SqlElement


class OrderingTerm(SqlElement):
    """Base class for ordering terms."""

    pass


class OrderingTermWithNulls(OrderingTerm):
    """Ordering term with NULLS FIRST/LAST."""

    def __init__(self, prev: SqlElement, nulls_first: bool) -> None:
        self._prev = prev
        self._nulls_first = nulls_first

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        if self._nulls_first:
            buffer.append(" NULLS FIRST")
        else:
            buffer.append(" NULLS LAST")
