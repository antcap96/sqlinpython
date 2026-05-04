from sqlinpython import col, With, TableRef, TableName, Select, Values
from sqlinpython.base import SqlElement
from sqlinpython.expression import literal, FunctionName
from sqlinpython.expression.function import WindowName, PartitionBy
from sqlinpython.table_or_subquery import (
    NestedFromClause,
    Subquery,
    TableFunctionRef,
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


def test_select_alias_star() -> None:
    # SELECT t.* FROM users t  — requires .Star on TableRefAliased (not yet implemented)
    aliased = TableRef("users").As("t", explicit_as=False)
    q = Select(aliased.Star).From(aliased)
    assert q.get_query() == "SELECT t.* FROM users t"


# def test_table_star_result_column2() -> None:
#     assert to_str(TableRef("users")["*"]) == "users.*"


# def test_table_star_result_column3() -> None:
#     assert to_str(TableRef("users").As("u")["*"]) == "u.*"


# def test_table_column() -> None:
#     assert to_str(TableRef("users").As("u")["id"]) == "u.id"


# ---------------------------------------------------------------------------
# TableFunctionRef
# ---------------------------------------------------------------------------


def test_table_function_ref() -> None:
    f = TableFunctionRef("json_each")(literal("[]"))
    assert to_str(f) == 'json_each("[]")'


def test_table_function_ref_aliased() -> None:
    f = TableFunctionRef("schema", "json_each")(literal("[]")).As("j")
    assert to_str(f) == 'schema.json_each("[]") AS j'


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
# Full query examples with more complex expressions
# ---------------------------------------------------------------------------


def test_complete_1() -> None:
    assert Select("*").From(TableRef("users")).get_query() == "SELECT * FROM users"


def test_complete_2() -> None:
    q = Select(col("id"), col("name"), col("email")).From(TableRef("users"))
    assert q.get_query() == "SELECT id, name, email FROM users"


def test_complete_3() -> None:
    q = Select("*").From(TableRef("users")).Where(col("age") > literal(18))
    assert q.get_query() == "SELECT * FROM users WHERE age > 18"


def test_complete_4() -> None:
    q = Select(
        col("first_name").As("name"),
        (col("salary") * literal(12)).As("annual_salary"),
    ).From(TableRef("employees"))
    assert q.get_query() == (
        "SELECT first_name AS name, salary * 12 AS annual_salary FROM employees"
    )


def test_complete_5() -> None:
    q = Select(col("orders", "id"), col("users", "name")).From(
        TableRef("orders")
        .Join(TableRef("users"))
        .On(col("orders", "user_id").eq(col("users", "id")))
    )
    assert q.get_query() == (
        "SELECT orders.id, users.name FROM orders JOIN users ON orders.user_id = users.id"
    )


def test_complete_6() -> None:
    q = (
        Select(col("department"), FunctionName("COUNT")("*").As("headcount"))
        .From(TableRef("employees"))
        .GroupBy(col("department"))
    )
    assert q.get_query() == (
        "SELECT department, COUNT(*) AS headcount FROM employees GROUP BY department"
    )


def test_complete_7() -> None:
    q = (
        Select(
            col("department"),
            FunctionName("AVG")(col("salary")).As("avg_salary"),
        )
        .From(TableRef("employees"))
        .GroupBy(col("department"))
        .Having(FunctionName("AVG")(col("salary")) > literal(50000))
    )
    assert q.get_query() == (
        "SELECT department, AVG(salary) AS avg_salary "
        "FROM employees "
        "GROUP BY department "
        "HAVING AVG(salary) > 50000"
    )


def test_complete_8() -> None:
    q = (
        Select(col("name"))
        .From(TableRef("employees"))
        .Where(
            col("department_id").In(
                Select(col("id"))
                .From(TableRef("departments"))
                .Where(col("location").eq(literal("NYC")))
            )
        )
    )
    assert q.get_query() == (
        "SELECT name FROM employees "
        'WHERE department_id IN (SELECT id FROM departments WHERE location = "NYC")'
    )


def test_complete_9() -> None:
    q = (
        Select(col("u", "name"), col("o", "id").As("order_id"))
        .From(
            TableRef("users")
            .As("u", explicit_as=False)
            .LeftJoin(TableRef("orders").As("o", explicit_as=False))
            .On(col("u", "id").eq(col("o", "user_id")))
        )
        .Where(col("o", "id").IsNull)
    )
    assert q.get_query() == (
        "SELECT u.name, o.id AS order_id "
        "FROM users u "
        "LEFT JOIN orders o ON u.id = o.user_id "
        "WHERE o.id ISNULL"
    )


def test_complete_10() -> None:
    q = Select(
        col("name"),
        col("salary"),
        FunctionName("RANK")()
        .Over(PartitionBy(col("department")).OrderBy(col("salary").Desc))
        .As("rank"),
    ).From(TableRef("employees"))

    assert q.get_query() == (
        "SELECT name, salary, "
        "RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank "
        "FROM employees"
    )


def test_complete_11() -> None:
    avg = FunctionName("AVG")
    q = (
        With(
            TableName("dept_avg").As(
                Select(
                    col("department_id"),
                    avg(col("salary")).As("avg_salary"),
                )
                .From(TableRef("employees"))
                .GroupBy(col("department_id"))
            )
        )
        .Select(
            col("e", "name"),
            col("e", "salary"),
            col("d", "avg_salary"),
        )
        .From(
            TableRef("employees")
            .As("e", explicit_as=False)
            .Join(TableRef("dept_avg").As("d", explicit_as=False))
            .On(col("e", "department_id").eq(col("d", "department_id")))
        )
        .Where(col("e", "salary") > col("d", "avg_salary"))
    )

    assert q.get_query() == (
        "WITH dept_avg AS ("
        "SELECT department_id, AVG(salary) AS avg_salary "
        "FROM employees "
        "GROUP BY department_id"
        ") "
        "SELECT e.name, e.salary, d.avg_salary "
        "FROM employees e "
        "JOIN dept_avg d ON e.department_id = d.department_id "
        "WHERE e.salary > d.avg_salary"
    )


def test_complete_12() -> None:
    q = (
        With.Recursive(
            TableName("org_chart")("id", "name", "level").As(
                Select(col("id"), col("name"), literal(0))
                .From(TableRef("employees"))
                .Where(col("manager_id").IsNull)
                .UnionAll(
                    Select(
                        col("e", "id"),
                        col("e", "name"),
                        col("o", "level") + literal(1),
                    ).From(
                        TableRef("employees")
                        .As("e", explicit_as=False)
                        .Join(TableRef("org_chart").As("o", explicit_as=False))
                        .On(col("e", "manager_id").eq(col("o", "id")))
                    )
                )
            )
        )
        .Select(col("id"), col("name"), col("level"))
        .From(TableRef("org_chart"))
        .OrderBy(col("level"), col("name"))
    )

    assert q.get_query() == (
        "WITH RECURSIVE org_chart(id, name, level) AS ("
        "SELECT id, name, 0 FROM employees WHERE manager_id ISNULL "
        "UNION ALL "
        "SELECT e.id, e.name, o.level + 1 "
        "FROM employees e "
        "JOIN org_chart o ON e.manager_id = o.id"
        ") "
        "SELECT id, name, level FROM org_chart ORDER BY level, name"
    )


def test_complete_13() -> None:
    avg = FunctionName("AVG")
    count = FunctionName("COUNT")
    q = Select(avg(col("count"))).From(
        Select(col("id"), count("*")).From(TableRef("t")).GroupBy(col("id"))
    )

    assert (
        q.get_query()
        == "SELECT AVG(count) FROM (SELECT id, COUNT(*) FROM t GROUP BY id)"
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
