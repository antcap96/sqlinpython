from sqlinpython import expression as expr
from sqlinpython.expression.function import (
    FunctionName,
    Groups,
    OrderBy,
    PartitionBy,
    Range,
    Rows,
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


def test_frame_spec() -> None:
    SUM = FunctionName("SUM")
    a = expr.literal(1)
    b = expr.literal(2)

    assert to_str(SUM(a).Over(Rows.CurrentRow)) == "SUM(1) OVER (ROWS CURRENT ROW)"
    assert to_str(SUM(a).Over(Range.CurrentRow)) == "SUM(1) OVER (RANGE CURRENT ROW)"
    assert to_str(SUM(a).Over(Groups.CurrentRow)) == "SUM(1) OVER (GROUPS CURRENT ROW)"
    assert (
        to_str(SUM(a).Over(OrderBy(a).Rows.CurrentRow))
        == "SUM(1) OVER (ORDER BY 1 ROWS CURRENT ROW)"
    )
    assert (
        to_str(SUM(a).Over(Rows.CurrentRow.ExcludeNoOthers))
        == "SUM(1) OVER (ROWS CURRENT ROW EXCLUDE NO OTHERS)"
    )
    assert (
        to_str(SUM(a).Over(Rows.CurrentRow.ExcludeCurrentRow))
        == "SUM(1) OVER (ROWS CURRENT ROW EXCLUDE CURRENT ROW)"
    )
    assert (
        to_str(SUM(a).Over(Rows.CurrentRow.ExcludeGroup))
        == "SUM(1) OVER (ROWS CURRENT ROW EXCLUDE GROUP)"
    )
    assert (
        to_str(SUM(a).Over(Rows.CurrentRow.ExcludeTies))
        == "SUM(1) OVER (ROWS CURRENT ROW EXCLUDE TIES)"
    )
    assert (
        to_str(SUM(a).Over(OrderBy(a).Rows.CurrentRow.ExcludeTies))
        == "SUM(1) OVER (ORDER BY 1 ROWS CURRENT ROW EXCLUDE TIES)"
    )
    assert (
        to_str(SUM(a).Over(Rows.UnboundedPreceding))
        == "SUM(1) OVER (ROWS UNBOUNDED PRECEDING)"
    )
    assert (
        to_str(SUM(a).Over(OrderBy(a).Rows.UnboundedPreceding.ExcludeTies))
        == "SUM(1) OVER (ORDER BY 1 ROWS UNBOUNDED PRECEDING EXCLUDE TIES)"
    )
    assert to_str(SUM(a).Over(Rows(a.Preceding))) == "SUM(1) OVER (ROWS 1 PRECEDING)"
    assert (
        to_str(SUM(a).Over(OrderBy(a).Rows(b.Preceding).ExcludeTies))
        == "SUM(1) OVER (ORDER BY 1 ROWS 2 PRECEDING EXCLUDE TIES)"
    )
    assert (
        to_str(SUM(a).Over(Range.Between.UnboundedPreceding.And.UnboundedFollowing))
        == "SUM(1) OVER (RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)"
    )
    assert (
        to_str(
            SUM(a).Over(
                OrderBy(
                    a
                ).Rows.Between.UnboundedPreceding.And.UnboundedFollowing.ExcludeTies
            )
        )
        == "SUM(1) OVER (ORDER BY 1 ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING EXCLUDE TIES)"
    )
    assert (
        to_str(SUM(a).Over(Rows.Between.CurrentRow.And.UnboundedFollowing))
        == "SUM(1) OVER (ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING)"
    )
    assert (
        to_str(SUM(a).Over(Rows.Between.UnboundedPreceding.And.CurrentRow))
        == "SUM(1) OVER (ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)"
    )
    assert (
        to_str(SUM(a).Over(Rows.Between.CurrentRow.And.CurrentRow))
        == "SUM(1) OVER (ROWS BETWEEN CURRENT ROW AND CURRENT ROW)"
    )
    assert (
        to_str(SUM(a).Over(Rows.Between(a.Preceding).And.CurrentRow))
        == "SUM(1) OVER (ROWS BETWEEN 1 PRECEDING AND CURRENT ROW)"
    )
    assert (
        to_str(SUM(a).Over(Rows.Between.CurrentRow.And(b.Following)))
        == "SUM(1) OVER (ROWS BETWEEN CURRENT ROW AND 2 FOLLOWING)"
    )
    assert (
        to_str(SUM(a).Over(Rows.Between(a.Preceding).And(b.Following)))
        == "SUM(1) OVER (ROWS BETWEEN 1 PRECEDING AND 2 FOLLOWING)"
    )
    assert (
        to_str(SUM(a).Over(Rows.Between(a.Following).And(b.Following).ExcludeTies))
        == "SUM(1) OVER (ROWS BETWEEN 1 FOLLOWING AND 2 FOLLOWING EXCLUDE TIES)"
    )
    assert (
        to_str(SUM(a).Over(WindowName("w").Rows.CurrentRow))
        == "SUM(1) OVER (w ROWS CURRENT ROW)"
    )
    assert (
        to_str(SUM(a).Over(PartitionBy(a).Rows.CurrentRow))
        == "SUM(1) OVER (PARTITION BY 1 ROWS CURRENT ROW)"
    )
