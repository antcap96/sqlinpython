from sqlinpython.ordering_term import OrderingTerm

from sqlinpython import expression as expr


def to_str(element: OrderingTerm) -> str:
    buffer: list[str] = []
    element._create_query(buffer)
    return "".join(buffer)


def test_ordering_term() -> None:
    assert to_str(expr.literal(1)) == "1"
    assert to_str(expr.literal(1).Collate("name")) == "1 COLLATE name"
    assert to_str(expr.literal(1).Asc) == "1 ASC"
    assert to_str(expr.literal(1).Desc) == "1 DESC"
    assert to_str(expr.literal(1).Collate("name").Asc) == "1 COLLATE name ASC"
    assert to_str(expr.literal(1).NullsFirst) == "1 NULLS FIRST"
    assert to_str(expr.literal(1).NullsLast) == "1 NULLS LAST"
    assert (
        to_str(expr.literal(1).Collate("name").NullsFirst)
        == "1 COLLATE name NULLS FIRST"
    )
    assert (
        to_str(expr.literal(1).Collate("name").Asc.NullsFirst)
        == "1 COLLATE name ASC NULLS FIRST"
    )
