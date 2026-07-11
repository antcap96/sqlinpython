# Typing and the public API

## The public surface

The public API is whatever is importable from one of:

- **`sqlinpython`** — statement entry points (`Select`, `Insert`, `Create`, …) and the building blocks (`col`, `literal`, `TableRef`, `Case`, `Cast`, `Not`, …).
- **`sqlinpython.functions`** — SQL function wrappers (`Avg`, `Count`, `Coalesce`, …).
- **`sqlinpython.types`** — statement result types (`SelectStatement`, `InsertStatement`, …) and expression types (`Expression`, `ExpressionOrLiteral`, …) for annotating your own query-building helpers.

Everything else — in particular the `sqlinpython.expression` subpackage and the intermediate builder types — is internal and may change without notice.

## Annotating your own helpers

`sqlinpython.types` exists so you can put types on functions that build or accept queries:

```python
from sqlinpython import Select, TableRef, col
from sqlinpython.types import Expression, SelectStatement

def active_users(condition: Expression) -> SelectStatement:
    return Select("*").From(TableRef("users")).Where(condition)

assert active_users(col("age") > 18).get_query() == "SELECT * FROM users WHERE age > 18"
```

`ExpressionOrLiteral` additionally admits bare Python values (`int`, `str`, `float`, `bool`, `bytes`, `None`), matching what most builder methods accept. The statement types also work with `isinstance`, and the statement/limited pairs nest — a plain UPDATE *is* an `UpdateStatementLimited`:

```python
from sqlinpython import Update
from sqlinpython.types import UpdateStatement, UpdateStatementLimited

q = Update("users").Set(column=1)
assert isinstance(q, UpdateStatement)
assert isinstance(q, UpdateStatementLimited)
```

## Intermediate builder types are not API

To only allow valid SQL syntax, the library creates hundreds of intermediate types — `Select(...)` has the type `SelectStatementWithSelectExpression`, `Select(...).From(...)` has `SelectStatementWithFrom`, and so on. These names are part of the public *behavior* (autocomplete and method chaining flow through them) but **not** part of the public API: don't write them in annotations; let the type checker infer them, or annotate with the `sqlinpython.types` result types where a complete statement is expected.

The payoff of all those types is that invalid SQL fails the type check. For example, `Explain(Explain(...))` is rejected by mypy/pyright/ty/pyrefly because `EXPLAIN` cannot wrap another `EXPLAIN`:

```python notest
Explain(Explain(Select(1)))  # type checker error — and not valid SQLite
```
