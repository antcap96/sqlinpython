from sqlinpython.base import SqlElement
from sqlinpython.name import Name


class IndexedColumn(SqlElement):
    def __init__(self, prev: SqlElement, asc: bool) -> None:
        self._prev = prev
        self._asc = asc

    def _create_query(self) -> str:
        asc_desc = "ASC" if self._asc else "DESC"
        return f"{self._prev._create_query()} {asc_desc}"


class IndexedColumnWithCollate(IndexedColumn):
    def __init__(self, prev: SqlElement, collate_name: Name) -> None:
        self._prev = prev
        self._collate_name = collate_name

    @property
    def Asc(self):
        return IndexedColumn(self, True)

    @property
    def Desc(self):
        return IndexedColumn(self, False)

    def _create_query(self) -> str:
        return (
            f"{self._prev._create_query()} COLLATE {self._collate_name._create_query()}"
        )
