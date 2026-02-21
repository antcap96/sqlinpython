from sqlinpython import expression as expr
from sqlinpython.expression.function import (
    FunctionName,
    OrderBy,
    PartitionBy,
    Star,
    WindowName,
)


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


def test_filter_clause() -> None:
    COUNT = FunctionName("COUNT")
    SUM = FunctionName("SUM")
    a = expr.literal(1)
    b = expr.literal(2)

    # Basic filter
    assert to_str(COUNT("*").FilterWhere(a > b)) == "COUNT(*) FILTER (WHERE 1 > 2)"

    # Filter with aggregate
    assert to_str(SUM(a).FilterWhere(b > a)) == "SUM(1) FILTER (WHERE 2 > 1)"

    # Filter in expression
    assert (
        to_str(COUNT("*").FilterWhere(a > b) + a) == "COUNT(*) FILTER (WHERE 1 > 2) + 1"
    )


def test_over_clause() -> None:
    SUM = FunctionName("SUM")
    ROW_NUMBER = FunctionName("ROW_NUMBER")
    a = expr.literal(1)
    b = expr.literal(2)

    # Empty OVER ()
    assert to_str(ROW_NUMBER().Over()) == "ROW_NUMBER() OVER ()"

    # OVER with window name
    assert to_str(SUM(a).Over(WindowName("w"))) == "SUM(1) OVER w"

    # OVER with PARTITION BY
    assert to_str(SUM(a).Over(PartitionBy(a))) == "SUM(1) OVER (PARTITION BY 1)"
    assert to_str(SUM(a).Over(PartitionBy(a, b))) == "SUM(1) OVER (PARTITION BY 1, 2)"

    # OVER with ORDER BY
    assert to_str(SUM(a).Over(OrderBy(a))) == "SUM(1) OVER (ORDER BY 1)"
    assert to_str(SUM(a).Over(OrderBy(a, b))) == "SUM(1) OVER (ORDER BY 1, 2)"
    assert to_str(SUM(a).Over(OrderBy(a.Desc))) == "SUM(1) OVER (ORDER BY 1 DESC)"

    # OVER with PARTITION BY and ORDER BY
    assert (
        to_str(SUM(a).Over(PartitionBy(b).OrderBy(a)))
        == "SUM(1) OVER (PARTITION BY 2 ORDER BY 1)"
    )
    assert (
        to_str(SUM(a).Over(PartitionBy(a, b).OrderBy(a.Desc, b.Asc)))
        == "SUM(1) OVER (PARTITION BY 1, 2 ORDER BY 1 DESC, 2 ASC)"
    )

    # OVER in expression
    assert to_str(SUM(a).Over(PartitionBy(b)) + a) == "SUM(1) OVER (PARTITION BY 2) + 1"

    assert (
        to_str(SUM(a).Over(WindowName("w").PartitionBy(b)))
        == "SUM(1) OVER (w PARTITION BY 2)"
    )
    assert (
        to_str(SUM(a).Over(WindowName("w").OrderBy(a))) == "SUM(1) OVER (w ORDER BY 1)"
    )
    assert (
        to_str(SUM(a).Over(WindowName("w").PartitionBy(b).OrderBy(a.Desc)))
        == "SUM(1) OVER (w PARTITION BY 2 ORDER BY 1 DESC)"
    )
    assert (
        to_str(SUM(a).FilterWhere(a > b).Over(PartitionBy(b)))
        == "SUM(1) FILTER (WHERE 1 > 2) OVER (PARTITION BY 2)"
    )
