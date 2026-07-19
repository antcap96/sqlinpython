# SELECT

A `SELECT` statement starts with the `Select` entry point, which takes the result columns, and grows clause by clause through method chaining. Call `get_query()` at any complete stage to render the SQL string.

Every code block on this page is executable — the `assert`s are checked by the test suite.

## Result columns

`Select` accepts expressions (built with [`col` and `literal`](./expressions.md)), the string `"*"` for all columns, and bare Python literals, which are converted to SQL literals:

```python
from sqlinpython import Select, TableRef, col

assert Select("*").From(TableRef("users")).get_query() == "SELECT * FROM users"
assert (
    Select(col("id"), col("name"), col("email")).From(TableRef("users")).get_query()
    == "SELECT id, name, email FROM users"
)
assert Select(col("a"), 1, "x").From(TableRef("t")).get_query() == "SELECT a, 1, 'x' FROM t"
```

`Select.Distinct` and `Select.All` produce `SELECT DISTINCT` and `SELECT ALL`:

```python
from sqlinpython import Select

assert Select.Distinct("*").get_query() == "SELECT DISTINCT *"
assert Select.All("*").get_query() == "SELECT ALL *"
```

Expressions are aliased with `.As`:

```python
from sqlinpython import Select, TableRef, col

q = Select(
    col("first_name").As("name"),
    (col("salary") * 12).As("annual_salary"),
).From(TableRef("employees"))
assert q.get_query() == (
    "SELECT first_name AS name, salary * 12 AS annual_salary FROM employees"
)
```

## FROM and joins

`From` takes one or more table sources. A plain table is a `TableRef`, which can be schema-qualified and aliased (`explicit_as=False` drops the `AS` keyword):

```python
from sqlinpython import Select, TableRef

assert Select("*").From(TableRef("a"), TableRef("b")).get_query() == "SELECT * FROM a, b"
assert (
    Select("*").From(TableRef("users").As("u")).get_query()
    == "SELECT * FROM users AS u"
)
```

Joins are built on the table source with `Join`, `LeftJoin`, etc., followed by `On` or `Using`. An aliased `TableRef` can be indexed with `["column"]` to produce qualified column references:

```python
from sqlinpython import Select, TableRef

o = TableRef("orders").As("o", explicit_as=False)
u = TableRef("users").As("u", explicit_as=False)
q = Select(o["id"], u["name"]).From(o.Join(u).On(o["user_id"] == u["id"]))
assert (
    q.get_query()
    == "SELECT o.id, u.name FROM orders o JOIN users u ON o.user_id = u.id"
)
```

The two-argument form `col("table", "column")` is an alternative way to qualify columns:

```python
from sqlinpython import Select, TableRef, col

q = (
    Select(col("u", "name"), col("o", "id").As("order_id"))
    .From(
        TableRef("users")
        .As("u", explicit_as=False)
        .LeftJoin(TableRef("orders").As("o", explicit_as=False))
        .On(col("u", "id") == col("o", "user_id"))
    )
    .Where(col("o", "id").IsNull)
)
assert q.get_query() == (
    "SELECT u.name, o.id AS order_id "
    + "FROM users u "
    + "LEFT JOIN orders o ON u.id = o.user_id "
    + "WHERE o.id ISNULL"
)
```

A subquery can be used directly as a table source:

```python
from sqlinpython import FunctionName, Select, TableRef, col

avg = FunctionName("AVG")
count = FunctionName("COUNT")
q = Select(avg(col("count"))).From(
    Select(col("id"), count("*")).From(TableRef("t")).GroupBy(col("id"))
)
assert q.get_query() == "SELECT AVG(count) FROM (SELECT id, COUNT(*) FROM t GROUP BY id)"
```

## WHERE

`Where` takes any expression — comparisons are built with Python operators (`==`, `<`, …) and methods like `.In`, `.IsNull` (see [Expressions](./expressions.md)):

```python
from sqlinpython import Select, TableRef, col

q = Select("*").From(TableRef("users")).Where(col("age") > 18)
assert q.get_query() == "SELECT * FROM users WHERE age > 18"
```

Subqueries work inside expressions, e.g. with `In`:

```python
from sqlinpython import Select, TableRef, col

q = (
    Select(col("name"))
    .From(TableRef("employees"))
    .Where(
        col("department_id").In(
            Select(col("id"))
            .From(TableRef("departments"))
            .Where(col("location") == "NYC")
        )
    )
)
assert q.get_query() == (
    "SELECT name FROM employees "
    + "WHERE department_id IN (SELECT id FROM departments WHERE location = 'NYC')"
)
```

## GROUP BY and HAVING

```python
from sqlinpython import FunctionName, Select, TableRef, col

q = (
    Select(col("department"), FunctionName("COUNT")("*").As("headcount"))
    .From(TableRef("employees"))
    .GroupBy(col("department"))
)
assert q.get_query() == (
    "SELECT department, COUNT(*) AS headcount FROM employees GROUP BY department"
)

q2 = (
    Select(col("department"), FunctionName("AVG")(col("salary")).As("avg_salary"))
    .From(TableRef("employees"))
    .GroupBy(col("department"))
    .Having(FunctionName("AVG")(col("salary")) > 50000)
)
assert q2.get_query() == (
    "SELECT department, AVG(salary) AS avg_salary "
    + "FROM employees "
    + "GROUP BY department "
    + "HAVING AVG(salary) > 50000"
)
```

## ORDER BY, LIMIT and OFFSET

Ordering direction and NULL placement are properties on the expression (`Asc`, `Desc`, `NullsFirst`, `NullsLast`). `Limit` and `Offset` accept expressions or bare Python ints:

```python
from sqlinpython import Select, TableRef, col

q = (
    Select("*")
    .From(TableRef("t"))
    .OrderBy(col("a").Asc, col("b").Desc)
    .Limit(10)
    .Offset(5)
)
assert q.get_query() == "SELECT * FROM t ORDER BY a ASC, b DESC LIMIT 10 OFFSET 5"
```

## Compound selects

Complete selects are combined with `Union`, `UnionAll`, `Intersect` and `Except`; ordering applies to the compound result:

```python
from sqlinpython import Select, TableRef, literal

a = Select("*").From(TableRef("a"))
b = Select("*").From(TableRef("b"))
assert a.Union(b).get_query() == "SELECT * FROM a UNION SELECT * FROM b"
assert a.UnionAll(b).get_query() == "SELECT * FROM a UNION ALL SELECT * FROM b"
assert a.Intersect(b).get_query() == "SELECT * FROM a INTERSECT SELECT * FROM b"
assert a.Except(b).get_query() == "SELECT * FROM a EXCEPT SELECT * FROM b"
assert (
    a.Union(b).OrderBy(literal(1).Asc).get_query()
    == "SELECT * FROM a UNION SELECT * FROM b ORDER BY 1 ASC"
)
```

## VALUES

`Values` is a select statement of its own and can appear anywhere a select can — including as a compound operand. Rows are tuples of expressions or bare Python literals:

```python
from sqlinpython import Select, TableRef, Values

assert Values((1, "a"), (2, "b")).get_query() == "VALUES (1, 'a'), (2, 'b')"
assert (
    Values((1,)).Union(Select("*").From(TableRef("b"))).get_query()
    == "VALUES (1) UNION SELECT * FROM b"
)
```

## WITH ... SELECT

Common table expressions prefix a select via the `With` entry point — see [Common table expressions](./cte.md) for the full syntax:

```python
from sqlinpython import Select, TableName, TableRef, With

cte = TableName("cte").As(Select("*").From(TableRef("t")))
q = With(cte).Select("*").From(TableRef("cte"))
assert q.get_query() == "WITH cte AS (SELECT * FROM t) SELECT * FROM cte"
```
