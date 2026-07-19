# Functions and window functions

## The `functions` module

`sqlinpython.functions` wraps SQLite's built-in functions with the correct arities. Arguments accept expressions or bare Python literals:

```python
from sqlinpython import Select, TableRef, col
from sqlinpython import functions as fn

q = (
    Select(col("department"), fn.Count("*"), fn.Avg(col("salary")))
    .From(TableRef("employees"))
    .GroupBy(col("department"))
    .Having(fn.Avg(col("salary")) >= 8.0)
)
assert q.get_query() == (
    "SELECT department, COUNT(*), AVG(salary) "
    + "FROM employees "
    + "GROUP BY department "
    + "HAVING AVG(salary) >= 8.0"
)
assert Select(fn.Coalesce(col("a"), 0)).get_query() == "SELECT COALESCE(a, 0)"
assert Select(fn.Substr(col("s"), 1, 3)).get_query() == "SELECT SUBSTR(s, 1, 3)"
```

## Arbitrary functions with `FunctionName`

Any function — user-defined or not yet wrapped — is called through `FunctionName`. It supports `*` (as the string or the `Star` object), `DISTINCT`, and an `ORDER BY` inside the call:

```python
from sqlinpython import FunctionName, Select, col

count = FunctionName("COUNT")
group_concat = FunctionName("GROUP_CONCAT")

assert Select(count("*")).get_query() == "SELECT COUNT(*)"
assert Select(count(col("a"), distinct=True)).get_query() == "SELECT COUNT(DISTINCT a)"
assert (
    Select(group_concat(col("name"), order_by=(col("name").Desc,))).get_query()
    == "SELECT GROUP_CONCAT(name ORDER BY name DESC)"
)
```

## FILTER

Aggregates take a `FILTER (WHERE ...)` clause via `FilterWhere`:

```python
from sqlinpython import Select, col
from sqlinpython import functions as fn

q = Select(fn.Count("*").FilterWhere(col("status") == "active"))
assert q.get_query() == "SELECT COUNT(*) FILTER (WHERE status = 'active')"
```

## OVER

`Over` turns a call into a window function. It accepts nothing (empty window), a `WindowName` referencing a [named window](./select.md), or a window definition built from `PartitionBy` / `OrderBy`:

```python
from sqlinpython import OrderBy, PartitionBy, Select, TableRef, WindowName, col
from sqlinpython import functions as fn

q = Select(
    col("name"),
    fn.Sum(col("salary")).Over(PartitionBy(col("department")).OrderBy(col("salary").Desc)),
).From(TableRef("employees"))
assert q.get_query() == (
    "SELECT name, SUM(salary) OVER (PARTITION BY department ORDER BY salary DESC) "
    + "FROM employees"
)

assert Select(fn.Sum(col("a")).Over()).get_query() == "SELECT SUM(a) OVER ()"
assert Select(fn.Sum(col("a")).Over(WindowName("w"))).get_query() == "SELECT SUM(a) OVER w"
assert Select(fn.Sum(col("a")).Over(OrderBy(col("b")))).get_query() == "SELECT SUM(a) OVER (ORDER BY b)"
```

`FilterWhere` and `Over` combine, in that order:

```python
from sqlinpython import PartitionBy, Select, col
from sqlinpython import functions as fn

q = Select(fn.Sum(col("x")).FilterWhere(col("x") > 0).Over(PartitionBy(col("g"))))
assert q.get_query() == "SELECT SUM(x) FILTER (WHERE x > 0) OVER (PARTITION BY g)"
```

## Frame specs

A window definition can end with a frame spec, started by `Rows`, `Range` or `Groups` (chained after `OrderBy`, or used standalone). Frame bounds are properties and calls — `expr.Preceding` / `expr.Following` build the `N PRECEDING` / `N FOLLOWING` bounds, and `Between ... And ...` covers the two-bound form:

```python
from sqlinpython import OrderBy, Rows, Select, col, literal
from sqlinpython import functions as fn

s = fn.Sum(col("a"))
one, two = literal(1), literal(2)

assert Select(s.Over(Rows.CurrentRow)).get_query() == "SELECT SUM(a) OVER (ROWS CURRENT ROW)"
assert (
    Select(s.Over(OrderBy(col("b")).Rows.UnboundedPreceding)).get_query()
    == "SELECT SUM(a) OVER (ORDER BY b ROWS UNBOUNDED PRECEDING)"
)
assert Select(s.Over(Rows(one.Preceding))).get_query() == "SELECT SUM(a) OVER (ROWS 1 PRECEDING)"
assert (
    Select(s.Over(Rows.Between.UnboundedPreceding.And.CurrentRow)).get_query()
    == "SELECT SUM(a) OVER (ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)"
)
assert (
    Select(s.Over(Rows.Between(one.Preceding).And(two.Following))).get_query()
    == "SELECT SUM(a) OVER (ROWS BETWEEN 1 PRECEDING AND 2 FOLLOWING)"
)
assert (
    Select(s.Over(Rows.CurrentRow.ExcludeTies)).get_query()
    == "SELECT SUM(a) OVER (ROWS CURRENT ROW EXCLUDE TIES)"
)
```
