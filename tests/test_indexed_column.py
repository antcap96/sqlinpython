import sqlinpython.expression as expr
from sqlinpython import ColumnName
from sqlinpython.base import SqlElement


def create_query(element: SqlElement) -> str:
    buffer: list[str] = []
    element._create_query(buffer)
    return "".join(buffer)


def test_indexed_column() -> None:
    a = ColumnName("a")
    assert create_query(a) == "a"
    assert create_query(a.Collate("b")) == "a COLLATE b"
    assert create_query(a.Asc) == "a ASC"
    assert create_query(a.Desc) == "a DESC"
    assert create_query(a.Collate("b").Asc) == "a COLLATE b ASC"
    assert create_query(expr.literal(1)) == "1"
    assert create_query(expr.literal(1).Collate("b")) == "1 COLLATE b"
    assert create_query(expr.literal(1).Collate("b").Asc) == "1 COLLATE b ASC"
    assert create_query(expr.literal(1).Collate("b").Desc) == "1 COLLATE b DESC"
