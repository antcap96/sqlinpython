from sqlinpython import (
    FunctionName,
    Groups,
    OrderBy,
    PartitionBy,
    Range,
    Rows,
    Star,
    WindowName,
    literal,
)
from sqlinpython import expression as expr

MAX = FunctionName("MAX")
COUNT = FunctionName("COUNT")
SUM = FunctionName("SUM")
GROUP_CONCAT = FunctionName("GROUP_CONCAT")
ROW_NUMBER = FunctionName("ROW_NUMBER")
one = literal(1)
two = literal(2)


def to_str(element: expr.Expression) -> str:
    buffer: list[str] = []
    element._create_query(buffer)
    return "".join(buffer)


# ---------------------------------------------------------------------------
# Function calls
# ---------------------------------------------------------------------------


def test_function_call_multiple_args() -> None:
    assert to_str(MAX(one, two)) == "MAX(1, 2)"


def test_function_call_no_args() -> None:
    assert to_str(COUNT()) == "COUNT()"


def test_function_call_star_string() -> None:
    assert to_str(COUNT("*")) == "COUNT(*)"


def test_function_call_star_object() -> None:
    assert to_str(COUNT(Star)) == "COUNT(*)"


def test_function_call_distinct() -> None:
    assert to_str(COUNT(one, two, distinct=True)) == "COUNT(DISTINCT 1, 2)"


def test_function_call_order_by() -> None:
    assert to_str(GROUP_CONCAT(one, order_by=(two,))) == "GROUP_CONCAT(1 ORDER BY 2)"


def test_function_call_order_by_desc() -> None:
    assert (
        to_str(GROUP_CONCAT(one, order_by=(two.Desc,)))
        == "GROUP_CONCAT(1 ORDER BY 2 DESC)"
    )


def test_function_call_distinct_order_by() -> None:
    assert (
        to_str(COUNT(one, two, distinct=True, order_by=(one,)))
        == "COUNT(DISTINCT 1, 2 ORDER BY 1)"
    )


def test_function_call_in_expression() -> None:
    assert to_str(MAX(one, two) + one) == "MAX(1, 2) + 1"


# ---------------------------------------------------------------------------
# FILTER clause
# ---------------------------------------------------------------------------


def test_filter_where_basic() -> None:
    assert to_str(COUNT("*").FilterWhere(one > two)) == "COUNT(*) FILTER (WHERE 1 > 2)"


def test_filter_where_aggregate() -> None:
    assert to_str(SUM(one).FilterWhere(two > one)) == "SUM(1) FILTER (WHERE 2 > 1)"


def test_filter_where_in_expression() -> None:
    assert (
        to_str(COUNT("*").FilterWhere(one > two) + one)
        == "COUNT(*) FILTER (WHERE 1 > 2) + 1"
    )


# ---------------------------------------------------------------------------
# OVER clause
# ---------------------------------------------------------------------------


def test_over_empty() -> None:
    assert to_str(ROW_NUMBER().Over()) == "ROW_NUMBER() OVER ()"


def test_over_window_name() -> None:
    assert to_str(SUM(one).Over(WindowName("w"))) == "SUM(1) OVER w"


def test_over_partition_by_single() -> None:
    assert to_str(SUM(one).Over(PartitionBy(one))) == "SUM(1) OVER (PARTITION BY 1)"


def test_over_partition_by_multiple() -> None:
    assert (
        to_str(SUM(one).Over(PartitionBy(one, two)))
        == "SUM(1) OVER (PARTITION BY 1, 2)"
    )


def test_over_order_by_single() -> None:
    assert to_str(SUM(one).Over(OrderBy(one))) == "SUM(1) OVER (ORDER BY 1)"


def test_over_order_by_multiple() -> None:
    assert to_str(SUM(one).Over(OrderBy(one, two))) == "SUM(1) OVER (ORDER BY 1, 2)"


def test_over_order_by_desc() -> None:
    assert to_str(SUM(one).Over(OrderBy(one.Desc))) == "SUM(1) OVER (ORDER BY 1 DESC)"


def test_over_partition_by_and_order_by() -> None:
    assert (
        to_str(SUM(one).Over(PartitionBy(two).OrderBy(one)))
        == "SUM(1) OVER (PARTITION BY 2 ORDER BY 1)"
    )


def test_over_partition_by_multiple_order_by_multiple() -> None:
    assert (
        to_str(SUM(one).Over(PartitionBy(one, two).OrderBy(one.Desc, two.Asc)))
        == "SUM(1) OVER (PARTITION BY 1, 2 ORDER BY 1 DESC, 2 ASC)"
    )


def test_over_in_expression() -> None:
    assert (
        to_str(SUM(one).Over(PartitionBy(two)) + one)
        == "SUM(1) OVER (PARTITION BY 2) + 1"
    )


def test_over_window_name_partition_by() -> None:
    assert (
        to_str(SUM(one).Over(WindowName("w").PartitionBy(two)))
        == "SUM(1) OVER (w PARTITION BY 2)"
    )


def test_over_window_name_order_by() -> None:
    assert (
        to_str(SUM(one).Over(WindowName("w").OrderBy(one)))
        == "SUM(1) OVER (w ORDER BY 1)"
    )


def test_over_window_name_partition_by_order_by() -> None:
    assert (
        to_str(SUM(one).Over(WindowName("w").PartitionBy(two).OrderBy(one.Desc)))
        == "SUM(1) OVER (w PARTITION BY 2 ORDER BY 1 DESC)"
    )


def test_over_filter_where_partition_by() -> None:
    assert (
        to_str(SUM(one).FilterWhere(one > two).Over(PartitionBy(two)))
        == "SUM(1) FILTER (WHERE 1 > 2) OVER (PARTITION BY 2)"
    )


# ---------------------------------------------------------------------------
# Frame spec
# ---------------------------------------------------------------------------


def test_frame_spec_rows_current_row() -> None:
    assert to_str(SUM(one).Over(Rows.CurrentRow)) == "SUM(1) OVER (ROWS CURRENT ROW)"


def test_frame_spec_range_current_row() -> None:
    assert to_str(SUM(one).Over(Range.CurrentRow)) == "SUM(1) OVER (RANGE CURRENT ROW)"


def test_frame_spec_groups_current_row() -> None:
    assert (
        to_str(SUM(one).Over(Groups.CurrentRow)) == "SUM(1) OVER (GROUPS CURRENT ROW)"
    )


def test_frame_spec_order_by_rows_current_row() -> None:
    assert (
        to_str(SUM(one).Over(OrderBy(one).Rows.CurrentRow))
        == "SUM(1) OVER (ORDER BY 1 ROWS CURRENT ROW)"
    )


def test_frame_spec_exclude_no_others() -> None:
    assert (
        to_str(SUM(one).Over(Rows.CurrentRow.ExcludeNoOthers))
        == "SUM(1) OVER (ROWS CURRENT ROW EXCLUDE NO OTHERS)"
    )


def test_frame_spec_exclude_current_row() -> None:
    assert (
        to_str(SUM(one).Over(Rows.CurrentRow.ExcludeCurrentRow))
        == "SUM(1) OVER (ROWS CURRENT ROW EXCLUDE CURRENT ROW)"
    )


def test_frame_spec_exclude_group() -> None:
    assert (
        to_str(SUM(one).Over(Rows.CurrentRow.ExcludeGroup))
        == "SUM(1) OVER (ROWS CURRENT ROW EXCLUDE GROUP)"
    )


def test_frame_spec_exclude_ties() -> None:
    assert (
        to_str(SUM(one).Over(Rows.CurrentRow.ExcludeTies))
        == "SUM(1) OVER (ROWS CURRENT ROW EXCLUDE TIES)"
    )


def test_frame_spec_order_by_rows_current_row_exclude_ties() -> None:
    assert (
        to_str(SUM(one).Over(OrderBy(one).Rows.CurrentRow.ExcludeTies))
        == "SUM(1) OVER (ORDER BY 1 ROWS CURRENT ROW EXCLUDE TIES)"
    )


def test_frame_spec_rows_unbounded_preceding() -> None:
    assert (
        to_str(SUM(one).Over(Rows.UnboundedPreceding))
        == "SUM(1) OVER (ROWS UNBOUNDED PRECEDING)"
    )


def test_frame_spec_order_by_rows_unbounded_preceding_exclude_ties() -> None:
    assert (
        to_str(SUM(one).Over(OrderBy(one).Rows.UnboundedPreceding.ExcludeTies))
        == "SUM(1) OVER (ORDER BY 1 ROWS UNBOUNDED PRECEDING EXCLUDE TIES)"
    )


def test_frame_spec_rows_expr_preceding() -> None:
    assert (
        to_str(SUM(one).Over(Rows(one.Preceding))) == "SUM(1) OVER (ROWS 1 PRECEDING)"
    )


def test_frame_spec_order_by_rows_expr_preceding_exclude_ties() -> None:
    assert (
        to_str(SUM(one).Over(OrderBy(one).Rows(two.Preceding).ExcludeTies))
        == "SUM(1) OVER (ORDER BY 1 ROWS 2 PRECEDING EXCLUDE TIES)"
    )


def test_frame_spec_between_unbounded_preceding_and_unbounded_following() -> None:
    assert (
        to_str(SUM(one).Over(Range.Between.UnboundedPreceding.And.UnboundedFollowing))
        == "SUM(1) OVER (RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)"
    )


def test_frame_spec_order_by_between_unbounded_exclude_ties() -> None:
    assert (
        to_str(
            SUM(one).Over(
                OrderBy(
                    one
                ).Rows.Between.UnboundedPreceding.And.UnboundedFollowing.ExcludeTies
            )
        )
        == "SUM(1) OVER (ORDER BY 1 ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING EXCLUDE TIES)"
    )


def test_frame_spec_between_current_row_and_unbounded_following() -> None:
    assert (
        to_str(SUM(one).Over(Rows.Between.CurrentRow.And.UnboundedFollowing))
        == "SUM(1) OVER (ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING)"
    )


def test_frame_spec_between_unbounded_preceding_and_current_row() -> None:
    assert (
        to_str(SUM(one).Over(Rows.Between.UnboundedPreceding.And.CurrentRow))
        == "SUM(1) OVER (ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)"
    )


def test_frame_spec_between_current_row_and_current_row() -> None:
    assert (
        to_str(SUM(one).Over(Rows.Between.CurrentRow.And.CurrentRow))
        == "SUM(1) OVER (ROWS BETWEEN CURRENT ROW AND CURRENT ROW)"
    )


def test_frame_spec_between_expr_preceding_and_current_row() -> None:
    assert (
        to_str(SUM(one).Over(Rows.Between(one.Preceding).And.CurrentRow))
        == "SUM(1) OVER (ROWS BETWEEN 1 PRECEDING AND CURRENT ROW)"
    )


def test_frame_spec_between_current_row_and_expr_following() -> None:
    assert (
        to_str(SUM(one).Over(Rows.Between.CurrentRow.And(two.Following)))
        == "SUM(1) OVER (ROWS BETWEEN CURRENT ROW AND 2 FOLLOWING)"
    )


def test_frame_spec_between_expr_preceding_and_expr_following() -> None:
    assert (
        to_str(SUM(one).Over(Rows.Between(one.Preceding).And(two.Following)))
        == "SUM(1) OVER (ROWS BETWEEN 1 PRECEDING AND 2 FOLLOWING)"
    )


def test_frame_spec_between_expr_following_and_expr_following_exclude_ties() -> None:
    assert (
        to_str(
            SUM(one).Over(Rows.Between(one.Following).And(two.Following).ExcludeTies)
        )
        == "SUM(1) OVER (ROWS BETWEEN 1 FOLLOWING AND 2 FOLLOWING EXCLUDE TIES)"
    )


def test_frame_spec_window_name_rows_current_row() -> None:
    assert (
        to_str(SUM(one).Over(WindowName("w").Rows.CurrentRow))
        == "SUM(1) OVER (w ROWS CURRENT ROW)"
    )


def test_frame_spec_partition_by_rows_current_row() -> None:
    assert (
        to_str(SUM(one).Over(PartitionBy(one).Rows.CurrentRow))
        == "SUM(1) OVER (PARTITION BY 1 ROWS CURRENT ROW)"
    )
