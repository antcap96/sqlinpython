from sqlinpython.base import SqlElement
from sqlinpython.common_table_expression import TableName, With
from sqlinpython.expression import literal
from sqlinpython.expression.function import WindowName
from sqlinpython.select import Select, Values
from sqlinpython.table_or_subquery import (
    NestedFromClause,
    Subquery,
    TableFunctionRef,
    TableRef,
)


def to_str(element: SqlElement) -> str:
    buffer: list[str] = []
    element._create_query(buffer)
    return "".join(buffer)


# ---------------------------------------------------------------------------
# TableRef
# ---------------------------------------------------------------------------


def test_table_ref_simple() -> None:
    assert to_str(TableRef("users")) == "users"


def test_table_ref_schema() -> None:
    assert to_str(TableRef("main", "users")) == "main.users"


def test_table_ref_aliased() -> None:
    assert to_str(TableRef("users").As("u")) == "users AS u"


def test_table_ref_indexed_by() -> None:
    assert (
        to_str(TableRef("users").IndexedBy("idx_name")) == "users INDEXED BY idx_name"
    )


def test_table_ref_not_indexed() -> None:
    assert to_str(TableRef("users").NotIndexed) == "users NOT INDEXED"


def test_table_star_result_column() -> None:
    assert to_str(TableRef("users").Star) == "users.*"


# ---------------------------------------------------------------------------
# TableFunctionRef
# ---------------------------------------------------------------------------


def test_table_function_ref() -> None:
    f = TableFunctionRef("json_each")(literal("[]"))
    assert to_str(f) == 'json_each("[]")'


def test_table_function_ref_aliased() -> None:
    f = TableFunctionRef("json_each")(literal("[]")).As("j")
    assert to_str(f) == 'json_each("[]") AS j'


# ---------------------------------------------------------------------------
# Subquery
# ---------------------------------------------------------------------------


def test_subquery() -> None:
    inner = Select("*").From(TableRef("t"))
    assert to_str(Subquery(inner)) == "(SELECT * FROM t)"


def test_subquery_aliased() -> None:
    inner = Select("*").From(TableRef("t"))
    assert to_str(Subquery(inner).As("s")) == "(SELECT * FROM t) AS s"


# ---------------------------------------------------------------------------
# NestedFromClause
# ---------------------------------------------------------------------------


def test_nested_from_clause_tables() -> None:
    n = NestedFromClause((TableRef("a"), TableRef("b")))
    assert to_str(n) == "(a, b)"


def test_nested_from_clause_join() -> None:
    join = TableRef("a").Join(TableRef("b")).On(literal(1))
    assert to_str(NestedFromClause(join)) == "(a JOIN b ON 1)"


# ---------------------------------------------------------------------------
# Join types
# ---------------------------------------------------------------------------


def test_join_on() -> None:
    assert to_str(TableRef("a").Join(TableRef("b")).On(literal(1))) == "a JOIN b ON 1"


def test_join_using() -> None:
    assert (
        to_str(TableRef("a").Join(TableRef("b")).Using("id")) == "a JOIN b USING (id)"
    )


def test_left_join() -> None:
    assert (
        to_str(TableRef("a").LeftJoin(TableRef("b")).On(literal(1)))
        == "a LEFT JOIN b ON 1"
    )


def test_left_outer_join() -> None:
    j = TableRef("a").LeftOuterJoin(TableRef("b")).On(literal(1))
    assert to_str(j) == "a LEFT OUTER JOIN b ON 1"


def test_right_join() -> None:
    assert (
        to_str(TableRef("a").RightJoin(TableRef("b")).On(literal(1)))
        == "a RIGHT JOIN b ON 1"
    )


def test_right_outer_join() -> None:
    j = TableRef("a").RightOuterJoin(TableRef("b")).On(literal(1))
    assert to_str(j) == "a RIGHT OUTER JOIN b ON 1"


def test_full_join() -> None:
    assert (
        to_str(TableRef("a").FullJoin(TableRef("b")).On(literal(1)))
        == "a FULL JOIN b ON 1"
    )


def test_full_outer_join() -> None:
    j = TableRef("a").FullOuterJoin(TableRef("b")).On(literal(1))
    assert to_str(j) == "a FULL OUTER JOIN b ON 1"


def test_inner_join() -> None:
    assert (
        to_str(TableRef("a").InnerJoin(TableRef("b")).On(literal(1)))
        == "a INNER JOIN b ON 1"
    )


def test_cross_join() -> None:
    assert (
        to_str(TableRef("a").CrossJoin(TableRef("b")).On(literal(1)))
        == "a CROSS JOIN b ON 1"
    )


def test_natural_join() -> None:
    assert to_str(TableRef("a").NaturalJoin(TableRef("b"))) == "a NATURAL JOIN b"


def test_natural_left_join() -> None:
    assert (
        to_str(TableRef("a").NaturalLeftJoin(TableRef("b"))) == "a NATURAL LEFT JOIN b"
    )


def test_natural_left_outer_join() -> None:
    j = TableRef("a").NaturalLeftOuterJoin(TableRef("b"))
    assert to_str(j) == "a NATURAL LEFT OUTER JOIN b"


def test_natural_right_join() -> None:
    assert (
        to_str(TableRef("a").NaturalRightJoin(TableRef("b")))
        == "a NATURAL RIGHT JOIN b"
    )


def test_natural_right_outer_join() -> None:
    j = TableRef("a").NaturalRightOuterJoin(TableRef("b"))
    assert to_str(j) == "a NATURAL RIGHT OUTER JOIN b"


def test_natural_full_join() -> None:
    assert (
        to_str(TableRef("a").NaturalFullJoin(TableRef("b"))) == "a NATURAL FULL JOIN b"
    )


def test_natural_full_outer_join() -> None:
    j = TableRef("a").NaturalFullOuterJoin(TableRef("b"))
    assert to_str(j) == "a NATURAL FULL OUTER JOIN b"


def test_natural_inner_join() -> None:
    assert (
        to_str(TableRef("a").NaturalInnerJoin(TableRef("b")))
        == "a NATURAL INNER JOIN b"
    )


def test_chained_joins() -> None:
    j = (
        TableRef("a")
        .Join(TableRef("b"))
        .On(literal(1))
        .LeftJoin(TableRef("c"))
        .On(literal(2))
    )
    assert to_str(j) == "a JOIN b ON 1 LEFT JOIN c ON 2"


# ---------------------------------------------------------------------------
# SELECT *
# ---------------------------------------------------------------------------


def test_select_star() -> None:
    assert Select("*").get_query() == "SELECT *"


def test_select_multiple_cols() -> None:
    assert Select(literal(1), literal(2)).get_query() == "SELECT 1, 2"


def test_select_distinct() -> None:
    assert Select.Distinct("*").get_query() == "SELECT DISTINCT *"


def test_select_all() -> None:
    assert Select.All("*").get_query() == "SELECT ALL *"


# ---------------------------------------------------------------------------
# FROM clause
# ---------------------------------------------------------------------------


def test_select_from_single() -> None:
    assert Select("*").From(TableRef("users")).get_query() == "SELECT * FROM users"


def test_select_from_multiple() -> None:
    q = Select("*").From(TableRef("a"), TableRef("b"))
    assert q.get_query() == "SELECT * FROM a, b"


def test_select_from_join() -> None:
    join = TableRef("a").Join(TableRef("b")).On(literal(1))
    q = Select("*").From(join)
    assert q.get_query() == "SELECT * FROM a JOIN b ON 1"


def test_select_from_aliased_table() -> None:
    q = Select("*").From(TableRef("users").As("u"))
    assert q.get_query() == "SELECT * FROM users AS u"


# ---------------------------------------------------------------------------
# WHERE clause
# ---------------------------------------------------------------------------


def test_select_where() -> None:
    q = Select("*").From(TableRef("t")).Where(literal(1))
    assert q.get_query() == "SELECT * FROM t WHERE 1"


# ---------------------------------------------------------------------------
# GROUP BY / HAVING
# ---------------------------------------------------------------------------


def test_select_group_by() -> None:
    q = Select("*").From(TableRef("t")).GroupBy(literal(1))
    assert q.get_query() == "SELECT * FROM t GROUP BY 1"


def test_select_group_by_multiple() -> None:
    q = Select("*").From(TableRef("t")).GroupBy(literal(1), literal(2))
    assert q.get_query() == "SELECT * FROM t GROUP BY 1, 2"


def test_select_having() -> None:
    q = Select("*").From(TableRef("t")).GroupBy(literal(1)).Having(literal(1))
    assert q.get_query() == "SELECT * FROM t GROUP BY 1 HAVING 1"


# ---------------------------------------------------------------------------
# WINDOW clause
# ---------------------------------------------------------------------------


def test_select_window() -> None:
    win = WindowName("w")
    q = Select("*").From(TableRef("t")).Window(("w", win))
    assert q.get_query() == "SELECT * FROM t WINDOW w AS (w)"


# ---------------------------------------------------------------------------
# ORDER BY
# ---------------------------------------------------------------------------


def test_select_order_by() -> None:
    q = Select("*").From(TableRef("t")).OrderBy(literal(1).Asc)
    assert q.get_query() == "SELECT * FROM t ORDER BY 1 ASC"


def test_select_order_by_multiple() -> None:
    q = Select("*").From(TableRef("t")).OrderBy(literal(1).Asc, literal(2).Desc)
    assert q.get_query() == "SELECT * FROM t ORDER BY 1 ASC, 2 DESC"


# ---------------------------------------------------------------------------
# LIMIT / OFFSET
# ---------------------------------------------------------------------------


def test_select_limit() -> None:
    q = Select("*").From(TableRef("t")).Limit(literal(10))
    assert q.get_query() == "SELECT * FROM t LIMIT 10"


def test_select_limit_offset() -> None:
    q = Select("*").From(TableRef("t")).Limit(literal(10)).Offset(literal(5))
    assert q.get_query() == "SELECT * FROM t LIMIT 10 OFFSET 5"


def test_select_limit_comma_offset() -> None:
    q = Select("*").From(TableRef("t")).Limit(literal(10), literal(5))
    assert q.get_query() == "SELECT * FROM t LIMIT 10, 5"


# ---------------------------------------------------------------------------
# Compound selects
# ---------------------------------------------------------------------------


def test_union() -> None:
    q = Select("*").From(TableRef("a")).Union(Select("*").From(TableRef("b")))
    assert q.get_query() == "SELECT * FROM a UNION SELECT * FROM b"


def test_values_union() -> None:
    q = Values((literal(1),)).Union(Select("*").From(TableRef("b")))
    assert q.get_query() == "VALUES (1) UNION SELECT * FROM b"


def test_union_all() -> None:
    q = Select("*").From(TableRef("a")).UnionAll(Select("*").From(TableRef("b")))
    assert q.get_query() == "SELECT * FROM a UNION ALL SELECT * FROM b"


def test_intersect() -> None:
    q = Select("*").From(TableRef("a")).Intersect(Select("*").From(TableRef("b")))
    assert q.get_query() == "SELECT * FROM a INTERSECT SELECT * FROM b"


def test_except() -> None:
    q = Select("*").From(TableRef("a")).Except(Select("*").From(TableRef("b")))
    assert q.get_query() == "SELECT * FROM a EXCEPT SELECT * FROM b"


def test_union_values_rhs() -> None:
    q = Select("*").From(TableRef("a")).Union(Values((literal(1), literal(2))))
    assert q.get_query() == "SELECT * FROM a UNION VALUES (1, 2)"


def test_multiple_unions_chained() -> None:
    q = (
        Select("*")
        .From(TableRef("a"))
        .Union(Select("*").From(TableRef("b")))
        .Union(Select("*").From(TableRef("c")))
    )
    assert (
        q.get_query() == "SELECT * FROM a UNION SELECT * FROM b UNION SELECT * FROM c"
    )


def test_multiple_unions_inner() -> None:
    q = (Select("*").From(TableRef("a")).Union(Select("*").From(TableRef("b")))).Union(
        Select("*").From(TableRef("c"))
    )
    assert (
        q.get_query() == "SELECT * FROM a UNION SELECT * FROM b UNION SELECT * FROM c"
    )


def test_compound_with_order_by() -> None:
    q = (
        Select("*")
        .From(TableRef("a"))
        .Union(Select("*").From(TableRef("b")))
        .OrderBy(literal(1).Asc)
    )
    assert q.get_query() == "SELECT * FROM a UNION SELECT * FROM b ORDER BY 1 ASC"


# ---------------------------------------------------------------------------
# VALUES
# ---------------------------------------------------------------------------


def test_values_single_row() -> None:
    q = Values((literal(1), literal(2)))
    assert q.get_query() == "VALUES (1, 2)"


def test_values_multiple_rows() -> None:
    q = Values((literal(1), literal(2)), (literal(3), literal(4)))
    assert q.get_query() == "VALUES (1, 2), (3, 4)"


def test_values_order_by() -> None:
    q = Values((literal(1),)).OrderBy(literal(1).Asc)
    assert q.get_query() == "VALUES (1) ORDER BY 1 ASC"


# ---------------------------------------------------------------------------
# WITH ... SELECT
# ---------------------------------------------------------------------------


def test_with_select() -> None:
    inner = Select("*").From(TableRef("t"))
    cte = TableName("cte").As(inner)
    q = With(cte).Select("*").From(TableRef("cte"))
    assert q.get_query() == "WITH cte AS (SELECT * FROM t) SELECT * FROM cte"


def test_with_values() -> None:
    cte = TableName("v").As(Values((literal(1),)))
    q = With(cte).Values((literal(2),))
    assert q.get_query() == "WITH v AS (VALUES (1)) VALUES (2)"


# ---------------------------------------------------------------------------
# Full query example
# ---------------------------------------------------------------------------


def test_full_select() -> None:
    q = (
        Select("*")
        .From(TableRef("users").As("u"))
        .Where(literal(1))
        .GroupBy(literal(2))
        .Having(literal(3))
        .OrderBy(literal(4).Asc)
        .Limit(literal(10))
        .Offset(literal(5))
    )
    assert (
        q.get_query()
        == "SELECT * FROM users AS u WHERE 1 GROUP BY 2 HAVING 3 ORDER BY 4 ASC LIMIT 10 OFFSET 5"
    )


# ---------------------------------------------------------------------------
# Type-level tests (verify type checkers reject invalid compound operands)
# ---------------------------------------------------------------------------


def test_union_rejects_ordered_subselect() -> None:
    _ = (
        Select("*")
        .From(TableRef("a"))
        .Union(
            Select("*").From(TableRef("b")).OrderBy(literal(1).Asc)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
            # ty doesn't currently identify this error -ty: ignore[invalid-argument-type]
        )
    )


def test_union_rejects_limited_subselect() -> None:
    _ = (
        Select("*")
        .From(TableRef("a"))
        .Union(
            Select("*").From(TableRef("b")).Limit(literal(10))  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
            # ty doesn't currently identify this error -ty: ignore[invalid-argument-type]
        )
    )
