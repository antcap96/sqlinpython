from sqlinpython.common_table_expression import (
    CommonTableExpression,
    SelectStatement,
    TableName,
)


def to_str(element: CommonTableExpression) -> str:
    buffer: list[str] = []
    element._create_query(buffer)
    return "".join(buffer)


select_stmt = SelectStatement()


def test_cte_basic() -> None:
    # table-name AS ( select-stmt )
    assert to_str(TableName("t1").As(select_stmt)) == "t1 AS (<select-stmt>)"


def test_cte_with_columns() -> None:
    # table-name ( column-name, ... ) AS ( select-stmt )
    assert to_str(TableName("t1")("a").As(select_stmt)) == "t1(a) AS (<select-stmt>)"
    assert (
        to_str(TableName("t1")("a", "b").As(select_stmt))
        == "t1(a, b) AS (<select-stmt>)"
    )
    assert (
        to_str(TableName("t1")("a", "b", "c").As(select_stmt))
        == "t1(a, b, c) AS (<select-stmt>)"
    )


def test_cte_materialized() -> None:
    # table-name AS MATERIALIZED ( select-stmt )
    assert (
        to_str(TableName("t1").As.Materialized(select_stmt))
        == "t1 AS MATERIALIZED (<select-stmt>)"
    )


def test_cte_not_materialized() -> None:
    # table-name AS NOT MATERIALIZED ( select-stmt )
    assert (
        to_str(TableName("t1").As.Not.Materialized(select_stmt))
        == "t1 AS NOT MATERIALIZED (<select-stmt>)"
    )


def test_cte_with_columns_and_materialized() -> None:
    # table-name ( column-name, ... ) AS MATERIALIZED ( select-stmt )
    assert (
        to_str(TableName("t1")("a", "b").As.Materialized(select_stmt))
        == "t1(a, b) AS MATERIALIZED (<select-stmt>)"
    )


def test_cte_with_columns_and_not_materialized() -> None:
    # table-name ( column-name, ... ) AS NOT MATERIALIZED ( select-stmt )
    assert (
        to_str(TableName("t1")("a", "b").As.Not.Materialized(select_stmt))
        == "t1(a, b) AS NOT MATERIALIZED (<select-stmt>)"
    )


def test_cte_quoted_names() -> None:
    # Names with special characters should be quoted
    assert (
        to_str(TableName("my table")("column 1").As(select_stmt))
        == '"my table"("column 1") AS (<select-stmt>)'
    )
