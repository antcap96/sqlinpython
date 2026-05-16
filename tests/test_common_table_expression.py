from sqlinpython import Select, TableName, TableRef, With
from sqlinpython.common_table_expression import (
    CommonTableExpression,
    WithClause,
)


def to_str(element: CommonTableExpression | WithClause) -> str:
    buffer: list[str] = []
    element._create_query(buffer)
    return "".join(buffer)


select_stmt = Select("*").From(TableRef("t"))
_expected = "SELECT * FROM t"


def test_cte_basic() -> None:
    # table-name AS ( select-stmt )
    assert to_str(TableName("t1").As(select_stmt)) == f"t1 AS ({_expected})"


def test_cte_with_one_column() -> None:
    # table-name ( column-name ) AS ( select-stmt )
    assert to_str(TableName("t1")("a").As(select_stmt)) == f"t1(a) AS ({_expected})"


def test_cte_with_two_columns() -> None:
    # table-name ( column-name, column-name ) AS ( select-stmt )
    assert (
        to_str(TableName("t1")("a", "b").As(select_stmt))
        == f"t1(a, b) AS ({_expected})"
    )


def test_cte_with_three_columns() -> None:
    # table-name ( column-name, column-name, column-name ) AS ( select-stmt )
    assert (
        to_str(TableName("t1")("a", "b", "c").As(select_stmt))
        == f"t1(a, b, c) AS ({_expected})"
    )


def test_cte_materialized() -> None:
    # table-name AS MATERIALIZED ( select-stmt )
    assert (
        to_str(TableName("t1").As.Materialized(select_stmt))
        == f"t1 AS MATERIALIZED ({_expected})"
    )


def test_cte_not_materialized() -> None:
    # table-name AS NOT MATERIALIZED ( select-stmt )
    assert (
        to_str(TableName("t1").As.Not.Materialized(select_stmt))
        == f"t1 AS NOT MATERIALIZED ({_expected})"
    )


def test_cte_with_columns_and_materialized() -> None:
    # table-name ( column-name, ... ) AS MATERIALIZED ( select-stmt )
    assert (
        to_str(TableName("t1")("a", "b").As.Materialized(select_stmt))
        == f"t1(a, b) AS MATERIALIZED ({_expected})"
    )


def test_cte_with_columns_and_not_materialized() -> None:
    # table-name ( column-name, ... ) AS NOT MATERIALIZED ( select-stmt )
    assert (
        to_str(TableName("t1")("a", "b").As.Not.Materialized(select_stmt))
        == f"t1(a, b) AS NOT MATERIALIZED ({_expected})"
    )


def test_cte_quoted_names() -> None:
    # Names with special characters should be quoted
    assert (
        to_str(TableName("my table")("column 1").As(select_stmt))
        == f'"my table"("column 1") AS ({_expected})'
    )


def test_with_single_cte() -> None:
    cte = TableName("t1").As(select_stmt)
    assert to_str(With(cte)) == f"WITH t1 AS ({_expected})"


def test_with_multiple_ctes() -> None:
    cte1 = TableName("t1").As(select_stmt)
    cte2 = TableName("t2")("a", "b").As(select_stmt)
    assert (
        to_str(With(cte1, cte2))
        == f"WITH t1 AS ({_expected}), t2(a, b) AS ({_expected})"
    )


def test_with_recursive_single_cte() -> None:
    cte = TableName("t1").As(select_stmt)
    assert to_str(With.Recursive(cte)) == f"WITH RECURSIVE t1 AS ({_expected})"


def test_with_recursive_multiple_ctes() -> None:
    cte1 = TableName("t1").As(select_stmt)
    cte2 = TableName("t2").As.Materialized(select_stmt)
    assert (
        to_str(With.Recursive(cte1, cte2))
        == f"WITH RECURSIVE t1 AS ({_expected}), t2 AS MATERIALIZED ({_expected})"
    )
