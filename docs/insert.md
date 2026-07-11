# INSERT and REPLACE

## INSERT ... VALUES

`Insert.Into` names the table (optionally `schema, table`, plus `.As` for an alias), a call names the columns, and `Values` takes one tuple per row. Bare Python values are converted to SQL literals:

```python
from sqlinpython import Insert

q = Insert.Into("users")("id", "name").Values((1, "Alice"), (2, "Bob"))
assert q.get_query() == "INSERT INTO users (id, name) VALUES (1, 'Alice'), (2, 'Bob')"

assert (
    Insert.Into("main", "users").As("u")("id").Values((1,)).get_query()
    == "INSERT INTO main.users AS u (id) VALUES (1)"
)
```

## INSERT ... SELECT and DEFAULT VALUES

Passing a select statement instead of column names (or after them) makes an `INSERT ... SELECT`; the `DefaultValues` property makes an `INSERT ... DEFAULT VALUES`:

```python
from sqlinpython import Insert, Select, TableRef

events = Select("*").From(TableRef("events"))
assert (
    Insert.Into("users")("id", "name")(events).get_query()
    == "INSERT INTO users (id, name) SELECT * FROM events"
)
assert Insert.Into("users").DefaultValues.get_query() == "INSERT INTO users DEFAULT VALUES"
```

## Conflict resolution: INSERT OR ... and REPLACE

The `OrAbort` / `OrFail` / `OrIgnore` / `OrReplace` / `OrRollback` properties insert the conflict-resolution keyword; `Replace` is its own entry point:

```python
from sqlinpython import Insert, Replace

assert (
    Insert.OrIgnore.Into("users")("id").Values((1,)).get_query()
    == "INSERT OR IGNORE INTO users (id) VALUES (1)"
)
assert (
    Replace.Into("users")("id").Values((1,)).get_query()
    == "REPLACE INTO users (id) VALUES (1)"
)
```

## Upsert: ON CONFLICT

`OnConflict` takes the conflict target as indexed columns (built from `ColumnName`, optionally with `Collate` / `Asc` / `Desc`), an optional `Where`, then `Do.Nothing` or `Do.UpdateSet`. Assignments are keyword arguments; a `(columns): expr` dict entry produces the column-list form:

```python
from sqlinpython import ColumnName, Insert

id_col = ColumnName("id")

q = (
    Insert.Into("users")("id", "name")
    .Values((1, "Alice"))
    .OnConflict(id_col)
    .Do.Nothing
)
assert q.get_query() == (
    "INSERT INTO users (id, name) VALUES (1, 'Alice') ON CONFLICT(id) DO NOTHING"
)

q2 = (
    Insert.Into("users")("id", "name")
    .Values((1, "Alice"))
    .OnConflict(id_col)
    .Do.UpdateSet(name="Updated")
    .Where(ColumnName("name").ne("Admin"))
)
assert q2.get_query() == (
    "INSERT INTO users (id, name) VALUES (1, 'Alice') "
    + "ON CONFLICT(id) DO UPDATE SET name = 'Updated' WHERE name != 'Admin'"
)

q3 = (
    Insert.Into("users")("id", "name", "email")
    .Values((1, "Alice", "a@b.com"))
    .OnConflict(id_col)
    .Do.UpdateSet({("name", "email"): "some_expr"})
)
assert q3.get_query() == (
    "INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'a@b.com') "
    + "ON CONFLICT(id) DO UPDATE SET (name, email) = 'some_expr'"
)
```

## RETURNING

`Returning` accepts `"*"`, expressions, and aliased expressions:

```python
from sqlinpython import ColumnName, Insert

q = Insert.Into("users")("id", "name").Values((1, "Alice")).Returning("*")
assert q.get_query() == "INSERT INTO users (id, name) VALUES (1, 'Alice') RETURNING *"

q2 = (
    Insert.Into("users")("id", "name")
    .Values((1, "Alice"))
    .Returning(ColumnName("id").As("user_id"))
)
assert q2.get_query() == (
    "INSERT INTO users (id, name) VALUES (1, 'Alice') RETURNING id AS user_id"
)
```

## WITH ... INSERT

A [WITH clause](./cte.md) can prefix INSERT and REPLACE:

```python
from sqlinpython import Insert, Select, TableName, TableRef, With

cte = TableName("recent").As(Select("*").From(TableRef("events")))
q = With(cte).Insert.Into("users")("id").Values((1,))
assert q.get_query() == "WITH recent AS (SELECT * FROM events) INSERT INTO users (id) VALUES (1)"
```
