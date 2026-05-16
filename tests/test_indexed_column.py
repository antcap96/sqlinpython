from sqlinpython import ColumnName, IndexedColumn, literal


def to_str(element: IndexedColumn) -> str:
    buffer: list[str] = []
    element._create_query(buffer)
    return "".join(buffer)


def test_indexed_column_name() -> None:
    a = ColumnName("a")
    assert to_str(a) == "a"


def test_indexed_column_collate() -> None:
    a = ColumnName("a")
    assert to_str(a.Collate("b")) == "a COLLATE b"


def test_indexed_column_asc() -> None:
    a = ColumnName("a")
    assert to_str(a.Asc) == "a ASC"


def test_indexed_column_desc() -> None:
    a = ColumnName("a")
    assert to_str(a.Desc) == "a DESC"


def test_indexed_column_collate_asc() -> None:
    a = ColumnName("a")
    assert to_str(a.Collate("b").Asc) == "a COLLATE b ASC"


def test_indexed_column_literal() -> None:
    assert to_str(literal(1)) == "1"


def test_indexed_column_literal_collate() -> None:
    assert to_str(literal(1).Collate("b")) == "1 COLLATE b"


def test_indexed_column_literal_collate_asc() -> None:
    assert to_str(literal(1).Collate("b").Asc) == "1 COLLATE b ASC"


def test_indexed_column_literal_collate_desc() -> None:
    assert to_str(literal(1).Collate("b").Desc) == "1 COLLATE b DESC"
