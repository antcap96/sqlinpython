from sqlinpython import expression as expr
from sqlinpython.expression.function import FunctionName, Star


def to_str(element: expr.Expression) -> str:
    buffer: list[str] = []
    element._create_query(buffer)
    return "".join(buffer)


def test_function_calls() -> None:
    MAX = FunctionName("MAX")
    COUNT = FunctionName("COUNT")
    GROUP_CONCAT = FunctionName("GROUP_CONCAT")
    a = expr.literal(1)
    b = expr.literal(2)

    # Basic
    assert to_str(MAX(a, b)) == "MAX(1, 2)"
    assert to_str(COUNT()) == "COUNT()"

    # Star
    assert to_str(COUNT("*")) == "COUNT(*)"
    assert to_str(COUNT(Star)) == "COUNT(*)"

    # Distinct
    assert to_str(COUNT(a, b, distinct=True)) == "COUNT(DISTINCT 1, 2)"

    # Order By
    assert to_str(GROUP_CONCAT(a, order_by=(b,))) == "GROUP_CONCAT(1 ORDER BY 2)"
    assert (
        to_str(GROUP_CONCAT(a, order_by=(b.Desc,))) == "GROUP_CONCAT(1 ORDER BY 2 DESC)"
    )

    # Distinct + Order By
    assert (
        to_str(COUNT(a, b, distinct=True, order_by=(a,)))
        == "COUNT(DISTINCT 1, 2 ORDER BY 1)"
    )

    # In expressions
    assert to_str(MAX(a, b) + a) == "MAX(1, 2) + 1"
