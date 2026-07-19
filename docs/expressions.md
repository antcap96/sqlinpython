# Expressions

Expressions are the values that appear in result columns, `WHERE` conditions, `SET` assignments and so on. The two workhorses are `col`, which references a column, and `literal`, which converts a Python value to a SQL literal. On this page expressions are rendered inside a `SELECT` so `get_query()` can be called on the result.

## Columns

`col` takes one, two or three arguments for `column`, `table.column` and `schema.table.column`:

```python
from sqlinpython import Select, col

assert Select(col("a")).get_query() == "SELECT a"
assert Select(col("t", "a")).get_query() == "SELECT t.a"
assert Select(col("s", "t", "a")).get_query() == "SELECT s.t.a"
```

Identifiers that are not plain identifier tokens are quoted automatically:

```python
from sqlinpython import Select, col

assert Select(col("my column")).get_query() == 'SELECT "my column"'
```

## Literals

`literal` accepts `int`, `float`, `str`, `bytes`, `bool` and `None`. String quoting (including embedded quotes) is handled for you:

```python
from sqlinpython import Select, literal

assert Select(literal(1)).get_query() == "SELECT 1"
assert Select(literal(1.5)).get_query() == "SELECT 1.5"
assert Select(literal("O'Reilly")).get_query() == "SELECT 'O''Reilly'"
assert Select(literal(b"\xff")).get_query() == "SELECT X'FF'"
assert Select(literal(True)).get_query() == "SELECT TRUE"
assert Select(literal(None)).get_query() == "SELECT NULL"
assert Select(literal(255, hex=True)).get_query() == "SELECT 0xFF"
```

Most APIs also coerce bare Python values, so `literal` is only needed where an `Expression` is required to start a chain. For exact numeric spellings (leading zeros, exponents, hex with separators) there is `NumericLiteral`, and `CurrentDate` / `CurrentTime` / `CurrentTimestamp` are provided as constants:

```python
from sqlinpython import CurrentTimestamp, NumericLiteral, Select

assert Select(NumericLiteral("1.5e10")).get_query() == "SELECT 1.5e10"
assert Select(CurrentTimestamp).get_query() == "SELECT CURRENT_TIMESTAMP"
```

## Operators and precedence

Python's arithmetic, comparison and bitwise operators are overloaded. The library knows SQLite's operator precedence and inserts parentheses exactly where the Python expression tree requires them:

```python
from sqlinpython import Select, literal

one, two = literal(1), literal(2)
assert Select(one + two * one).get_query() == "SELECT 1 + 2 * 1"
assert Select((one + two) * one).get_query() == "SELECT (1 + 2) * 1"
assert Select(one - (two - one)).get_query() == "SELECT 1 - (2 - 1)"
assert Select((one > two) - one).get_query() == "SELECT (1 > 2) - 1"
```

Bare Python values work on either side of an operator:

```python
from sqlinpython import Select, col

assert Select(col("a") + 2).get_query() == "SELECT a + 2"
assert Select(5 - col("a")).get_query() == "SELECT 5 - a"
```

Keyword operators that Python cannot overload are methods: `And`, `Or`, `Not(...)`, `Concat` (`||`), `Extract` (`->`) and `Extract2` (`->>`):

```python
from sqlinpython import Not, Select, col, literal

t, f = literal(True), literal(False)
assert Select(t.Or(f).And(t)).get_query() == "SELECT (TRUE OR FALSE) AND TRUE"
assert Select(Not(f)).get_query() == "SELECT NOT FALSE"
assert Select(literal("a").Concat("z")).get_query() == "SELECT 'a' || 'z'"
assert Select(col("doc").Extract2("$.id")).get_query() == "SELECT doc ->> '$.id'"
```

## Comparisons

`==` and `!=` build the SQL comparisons `=` and `!=`; the `eq` and `ne` methods remain for the alternative SQL spellings, chosen via flags:

```python
from sqlinpython import Select, col

assert Select(col("a") == 1).get_query() == "SELECT a = 1"
assert Select(col("a") != 1).get_query() == "SELECT a != 1"
assert Select(col("a").eq(1, double_eq=True)).get_query() == "SELECT a == 1"
assert Select(col("a").ne(1, arrows=True)).get_query() == "SELECT a <> 1"
```

Because comparison operators build SQL instead of returning `bool`, truth-testing an expression raises `TypeError`. This makes accidental Python-level uses fail loudly instead of silently misbehaving: `if a == b:`, `expr in some_list`, and chained comparisons like `0 <= col("a") <= 5` all raise (use `col("a").Between(0, 5)` instead). Python-level identity stays available via `is`, and expressions remain hashable by identity, so sets and dicts of expressions work as before.

The remaining SQL comparison forms are methods and properties, with `Not` variants chained through `.Not`:

```python
from sqlinpython import Select, col

assert Select(col("a").Between(0, 10)).get_query() == "SELECT a BETWEEN 0 AND 10"
assert Select(col("a").In(1, 2, 3)).get_query() == "SELECT a IN (1, 2, 3)"
assert Select(col("a").Not.In(1, 2)).get_query() == "SELECT a NOT IN (1, 2)"
assert Select(col("a").Like("%x%")).get_query() == "SELECT a LIKE '%x%'"
assert (
    Select(col("a").Like("50\\%").Escape("\\")).get_query()
    == "SELECT a LIKE '50\\%' ESCAPE '\\'"
)
assert Select(col("a").Glob("*.txt")).get_query() == "SELECT a GLOB '*.txt'"
assert Select(col("a").Is(None)).get_query() == "SELECT a IS NULL"
assert Select(col("a").Is.Not(None)).get_query() == "SELECT a IS NOT NULL"
assert Select(col("a").Is.DistinctFrom(1)).get_query() == "SELECT a IS DISTINCT FROM 1"
assert Select(col("a").IsNull).get_query() == "SELECT a ISNULL"
assert Select(col("a").Notnull).get_query() == "SELECT a NOTNULL"
```

## CASE

`Case` builds both the searched and the operand form; the expression ends with `.End`:

```python
from sqlinpython import Case, Select, col

q = Select(Case.When(col("a") == 1).Then("one").Else("other").End)
assert q.get_query() == "SELECT CASE WHEN a = 1 THEN 'one' ELSE 'other' END"

q2 = Select(Case(col("a")).When(1).Then("one").When(2).Then("two").End)
assert q2.get_query() == "SELECT CASE a WHEN 1 THEN 'one' WHEN 2 THEN 'two' END"
```

## CAST

`Cast` takes an expression and a type name — most easily one from `sqlinpython.types`; the raw `TypeName` builder (callable for parameterized types) covers anything the module doesn't:

```python
from sqlinpython import Cast, Select, TypeName, col, types

assert Select(Cast(col("a"), types.Integer)).get_query() == "SELECT CAST(a AS INTEGER)"
assert (
    Select(Cast(col("a"), types.Decimal(10, 2))).get_query()
    == "SELECT CAST(a AS DECIMAL(10, 2))"
)
assert (
    Select(Cast(col("a"), TypeName("VARCHAR")(10))).get_query()
    == "SELECT CAST(a AS VARCHAR(10))"
)
```

## Subqueries, EXISTS and row values

`ScalarSubquery` embeds a select statement as a value; `Exists` (and `Not.Exists`) test for rows; `Row` builds a parenthesized value list:

```python
from sqlinpython import Exists, Not, Row, ScalarSubquery, Select, TableRef, col

sub = Select(col("id")).From(TableRef("t"))
assert Select(ScalarSubquery(sub) == 1).get_query() == "SELECT (SELECT id FROM t) = 1"
assert Select(Exists(sub)).get_query() == "SELECT EXISTS (SELECT id FROM t)"
assert Select(Not.Exists(sub)).get_query() == "SELECT NOT EXISTS (SELECT id FROM t)"
assert Select(Row(1, 2).In(Row(1, 2), Row(3, 4))).get_query() == "SELECT (1, 2) IN ((1, 2), (3, 4))"
```

## Bind parameters

`BindParameter` covers all four SQLite parameter styles — positional, numbered, and named with `:`, `@` or `$`:

```python
from sqlinpython import BindParameter, Select, TableRef, col

assert (
    Select("*").From(TableRef("t")).Where(col("id") == BindParameter()).get_query()
    == "SELECT * FROM t WHERE id = ?"
)
assert Select(BindParameter(2)).get_query() == "SELECT ?2"
assert Select(BindParameter("id")).get_query() == "SELECT :id"
assert Select(BindParameter("id", "@")).get_query() == "SELECT @id"
assert Select(BindParameter("id", "$")).get_query() == "SELECT $id"
```

## RAISE

`Raise` is the special expression form usable in [trigger bodies](./create.md):

```python
from sqlinpython import Raise, Select

assert Select(Raise("IGNORE")).get_query() == "SELECT RAISE(IGNORE)"
assert Select(Raise("ABORT", "constraint failed")).get_query() == "SELECT RAISE(ABORT, 'constraint failed')"
```
