# UPDATE and DELETE

## UPDATE ... SET

`Update` names the table (optionally `schema, table`); `Set` takes assignments as keyword arguments (values are expressions or bare Python literals), or as a dict when the column name isn't a valid Python identifier — a tuple key produces the column-list form:

```python
from sqlinpython import Name, Update

assert Update("users").Set(column=1).get_query() == "UPDATE users SET column = 1"
assert (
    Update("main", "users").Set(column=1, other=2).get_query()
    == "UPDATE main.users SET column = 1, other = 2"
)
assert (
    Update("users").Set({Name("full name"): 1}).get_query()
    == 'UPDATE users SET "full name" = 1'
)
assert (
    Update("users").Set({("column", "other"): 1}).get_query()
    == "UPDATE users SET (column, other) = 1"
)
```

Conflict resolution uses the same `Or*` properties as [INSERT](./insert.md):

```python
from sqlinpython import Update

assert (
    Update.OrIgnore("users").Set(column=1).get_query()
    == "UPDATE OR IGNORE users SET column = 1"
)
```

## FROM, WHERE and RETURNING

SQLite's `UPDATE ... FROM` extension, the `WHERE` clause and `RETURNING` chain after `Set`:

```python
from sqlinpython import TableRef, Update, col

q = (
    Update("users")
    .Set(column=1)
    .From(TableRef("other"))
    .Where(col("users", "id") == col("other", "id"))
    .Returning("*")
)
assert q.get_query() == (
    "UPDATE users SET column = 1 FROM other WHERE users.id = other.id RETURNING *"
)
```

## ORDER BY and LIMIT (update-stmt-limited)

When SQLite is built with `SQLITE_ENABLE_UPDATE_DELETE_LIMIT`, UPDATE and DELETE accept `ORDER BY` / `LIMIT`. These produce the *limited* statement types (`UpdateStatementLimited` / `DeleteStatementLimited` in [`sqlinpython.typing`](./typing.md)):

```python
from sqlinpython import Update, literal

q = Update("users").Set(column=1).OrderBy(literal(1)).Limit(1)
assert q.get_query() == "UPDATE users SET column = 1 ORDER BY 1 LIMIT 1"
```

## DELETE

`Delete.From` names the table, then `Where` and `Returning` chain as usual. The table reference supports aliasing and index hints (`IndexedBy` / `NotIndexed`, also available on UPDATE):

```python
from sqlinpython import Delete, col

assert Delete.From("users").get_query() == "DELETE FROM users"
assert (
    Delete.From("users").Where(col("id") == 1).Returning("*").get_query()
    == "DELETE FROM users WHERE id = 1 RETURNING *"
)
assert (
    Delete.From("users").IndexedBy("idx_users").get_query()
    == "DELETE FROM users INDEXED BY idx_users"
)
```

## WITH ... UPDATE / DELETE

Both statements accept a [WITH clause](./cte.md) prefix:

```python
from sqlinpython import Select, TableName, With

cte = TableName("cte").As(Select(1))
assert (
    With(cte).Update("users").Set(column=1).get_query()
    == "WITH cte AS (SELECT 1) UPDATE users SET column = 1"
)
assert With(cte).Delete.From("users").get_query() == "WITH cte AS (SELECT 1) DELETE FROM users"
```
