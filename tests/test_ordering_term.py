from sqlinpython import OrderingTerm, literal


def to_str(element: OrderingTerm) -> str:
    buffer: list[str] = []
    element._create_query(buffer)
    return "".join(buffer)


def test_ordering_term_literal() -> None:
    assert to_str(literal(1)) == "1"


def test_ordering_term_collate() -> None:
    assert to_str(literal(1).Collate("name")) == "1 COLLATE name"


def test_ordering_term_asc() -> None:
    assert to_str(literal(1).Asc) == "1 ASC"


def test_ordering_term_desc() -> None:
    assert to_str(literal(1).Desc) == "1 DESC"


def test_ordering_term_collate_asc() -> None:
    assert to_str(literal(1).Collate("name").Asc) == "1 COLLATE name ASC"


def test_ordering_term_nulls_first() -> None:
    assert to_str(literal(1).NullsFirst) == "1 NULLS FIRST"


def test_ordering_term_nulls_last() -> None:
    assert to_str(literal(1).NullsLast) == "1 NULLS LAST"


def test_ordering_term_collate_nulls_first() -> None:
    assert to_str(literal(1).Collate("name").NullsFirst) == "1 COLLATE name NULLS FIRST"


def test_ordering_term_collate_asc_nulls_first() -> None:
    assert (
        to_str(literal(1).Collate("name").Asc.NullsFirst)
        == "1 COLLATE name ASC NULLS FIRST"
    )
