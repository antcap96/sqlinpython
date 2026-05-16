from sqlinpython import (
    FunctionName,
    PartitionBy,
    Select,
    TableName,
    TableRef,
    Values,
    WindowName,
    With,
    col,
    literal,
)

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


def test_select_alias_star() -> None:
    aliased = TableRef("users").As("t", explicit_as=False)
    q = Select(aliased.Star).From(aliased)
    assert q.get_query() == "SELECT t.* FROM users t"


def test_table_column_in_select_query() -> None:
    t = TableRef("users").As("u", explicit_as=False)
    q = Select(t["id"], t["name"]).From(t)
    assert q.get_query() == "SELECT u.id, u.name FROM users u"


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


def test_table_column_in_join() -> None:
    o = TableRef("orders").As("o", explicit_as=False)
    u = TableRef("users").As("u", explicit_as=False)
    q = Select(o["id"], u["name"]).From(o.Join(u).On(o["user_id"].eq(u["id"])))
    assert (
        q.get_query()
        == "SELECT o.id, u.name FROM orders o JOIN users u ON o.user_id = u.id"
    )


# ---------------------------------------------------------------------------
# WHERE clause
# ---------------------------------------------------------------------------


def test_select_where() -> None:
    q = Select("*").From(TableRef("t")).Where(literal(1))
    assert q.get_query() == "SELECT * FROM t WHERE 1"


def test_table_column_in_where_clause() -> None:
    t = TableRef("users").As("u", explicit_as=False)
    q = Select("*").From(t).Where(t["age"] > literal(18))
    assert q.get_query() == "SELECT * FROM users u WHERE u.age > 18"


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
# Full clause chain
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
# Complex queries
# ---------------------------------------------------------------------------


def test_select_col_helper() -> None:
    q = Select(col("id"), col("name"), col("email")).From(TableRef("users"))
    assert q.get_query() == "SELECT id, name, email FROM users"


def test_where_col_comparison() -> None:
    q = Select("*").From(TableRef("users")).Where(col("age") > literal(18))
    assert q.get_query() == "SELECT * FROM users WHERE age > 18"


def test_select_expression_aliases() -> None:
    q = Select(
        col("first_name").As("name"),
        (col("salary") * literal(12)).As("annual_salary"),
    ).From(TableRef("employees"))
    assert q.get_query() == (
        "SELECT first_name AS name, salary * 12 AS annual_salary FROM employees"
    )


def test_join_col_two_arg() -> None:
    q = Select(col("orders", "id"), col("users", "name")).From(
        TableRef("orders")
        .Join(TableRef("users"))
        .On(col("orders", "user_id").eq(col("users", "id")))
    )
    assert q.get_query() == (
        "SELECT orders.id, users.name FROM orders JOIN users ON orders.user_id = users.id"
    )


def test_group_by_count() -> None:
    q = (
        Select(col("department"), FunctionName("COUNT")("*").As("headcount"))
        .From(TableRef("employees"))
        .GroupBy(col("department"))
    )
    assert q.get_query() == (
        "SELECT department, COUNT(*) AS headcount FROM employees GROUP BY department"
    )


def test_having_avg() -> None:
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


def test_where_in_subquery() -> None:
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


def test_left_join_isnull() -> None:
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


def test_window_rank_partition() -> None:
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


def test_cte_with_join() -> None:
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


def test_recursive_cte() -> None:
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


def test_subquery_in_from() -> None:
    avg = FunctionName("AVG")
    count = FunctionName("COUNT")
    q = Select(avg(col("count"))).From(
        Select(col("id"), count("*")).From(TableRef("t")).GroupBy(col("id"))
    )

    assert (
        q.get_query()
        == "SELECT AVG(count) FROM (SELECT id, COUNT(*) FROM t GROUP BY id)"
    )
