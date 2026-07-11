# Common table expressions (WITH)

A CTE is defined with `TableName("name").As(select_stmt)`; the `With` entry point collects one or more of them and then continues into the statement they prefix — `Select`, `Values`, [`Insert` / `Replace`](./insert.md), [`Update` / `Delete`](./update-delete.md).

## Defining CTEs

Column names are an optional call between the table name and `As`; `Materialized` / `Not.Materialized` hints chain on `As`:

```python
from sqlinpython import Select, TableName, TableRef, With

inner = Select("*").From(TableRef("t"))

assert (
    With(TableName("t1").As(inner)).Select("*").From(TableRef("t1")).get_query()
    == "WITH t1 AS (SELECT * FROM t) SELECT * FROM t1"
)
assert (
    With(TableName("t1")("a", "b").As(inner)).Select("*").From(TableRef("t1")).get_query()
    == "WITH t1(a, b) AS (SELECT * FROM t) SELECT * FROM t1"
)
assert (
    With(TableName("t1").As.Materialized(inner)).Select("*").From(TableRef("t1")).get_query()
    == "WITH t1 AS MATERIALIZED (SELECT * FROM t) SELECT * FROM t1"
)
assert (
    With(TableName("t1").As.Not.Materialized(inner)).Select("*").From(TableRef("t1")).get_query()
    == "WITH t1 AS NOT MATERIALIZED (SELECT * FROM t) SELECT * FROM t1"
)
```

Note the two different classes at play: `TableName` is the CTE *definition* site (no schema, no alias), while `TableRef` is how the CTE is *referenced* in a FROM clause afterwards.

## Multiple CTEs

```python
from sqlinpython import Select, TableName, TableRef, With

q = (
    With(
        TableName("c1").As(Select(1)),
        TableName("c2").As(Select(2)),
    )
    .Select("*")
    .From(TableRef("c1"), TableRef("c2"))
)
assert q.get_query() == "WITH c1 AS (SELECT 1), c2 AS (SELECT 2) SELECT * FROM c1, c2"
```

## WITH RECURSIVE

`With.Recursive` marks the clause recursive; the classic pattern is a base query `UnionAll`-ed with the recursive step:

```python
from sqlinpython import Select, TableName, TableRef, With, col

q = (
    With.Recursive(
        TableName("cnt")("x").As(
            Select(1).UnionAll(
                Select(col("x") + 1).From(TableRef("cnt")).Where(col("x") < 10)
            )
        )
    )
    .Select(col("x"))
    .From(TableRef("cnt"))
)
assert q.get_query() == (
    "WITH RECURSIVE cnt(x) AS ("
    + "SELECT 1 UNION ALL SELECT x + 1 FROM cnt WHERE x < 10"
    + ") "
    + "SELECT x FROM cnt"
)
```

## CTEs on other statements

The object returned by `With(...)` exposes `Select`, `Values`, `Insert`, `Replace`, `Update` and `Delete`:

```python
from sqlinpython import Select, TableName, With

cte = TableName("cte").As(Select(1))
assert (
    With(cte).Insert.Into("users")("id").Values((1,)).get_query()
    == "WITH cte AS (SELECT 1) INSERT INTO users (id) VALUES (1)"
)
assert (
    With(cte).Update("users").Set(column=1).get_query()
    == "WITH cte AS (SELECT 1) UPDATE users SET column = 1"
)
assert (
    With(cte).Delete.From("users").get_query()
    == "WITH cte AS (SELECT 1) DELETE FROM users"
)
```
