# CREATE statements

All CREATE statements start from the `Create` entry point: `Create.Table`, `Create.Index`, `Create.View`, `Create.Trigger`, `Create.VirtualTable`. Modifiers like `Temp` / `Temporary`, `Unique` and `IfNotExists` slot in where SQLite's grammar puts them.

## CREATE TABLE

Calling the table with `ColumnDef` objects defines the columns; the type is attached by calling the column def with a `TypeName`:

```python
from sqlinpython import ColumnDef, Create, TypeName

q = Create.Table("users")(
    ColumnDef("id")(TypeName("INTEGER")),
    ColumnDef("name")(TypeName("TEXT")),
)
assert q.get_query() == "CREATE TABLE users (id INTEGER, name TEXT)"
```

Table options are trailing properties, and `Create.Table("schema", "name")` schema-qualifies:

```python
from sqlinpython import ColumnDef, Create

assert (
    Create.Table.IfNotExists("t")(ColumnDef("a")).WithoutRowId.get_query()
    == "CREATE TABLE IF NOT EXISTS t (a) WITHOUT ROWID"
)
assert Create.Table("t")(ColumnDef("a")).Strict.get_query() == "CREATE TABLE t (a) STRICT"
```

### Column constraints

Constraints chain onto the column definition: `PrimaryKey` (with `Asc`/`Desc`/`AutoIncrement`/`OnConflict.*`), `NotNull`, `Unique`, `Default`, `Check`, and `Constraint("name")` to name the next constraint:

```python
from sqlinpython import ColumnDef, Create, CurrentDate, TypeName, col

q = Create.Table("users")(
    ColumnDef("id")(TypeName("INTEGER")).PrimaryKey.AutoIncrement,
    ColumnDef("name")(TypeName("TEXT")).NotNull.Unique,
    ColumnDef("age")(TypeName("INTEGER")).Check(col("age") >= 0),
    ColumnDef("joined").Default(CurrentDate),
)
assert q.get_query() == (
    "CREATE TABLE users ("
    + "id INTEGER PRIMARY KEY AUTOINCREMENT, "
    + "name TEXT NOT NULL UNIQUE, "
    + "age INTEGER CHECK (age >= 0), "
    + "joined DEFAULT CURRENT_DATE"
    + ")"
)
```

### Foreign keys

A column-level foreign key starts with `References`; the referenced columns are a call, and `On.Update` / `On.Delete` actions, `Match` and deferrability chain after:

```python
from sqlinpython import ColumnDef, Create, TypeName

q = Create.Table("orders")(
    ColumnDef("user_id")(TypeName("INTEGER")).References("users")("id").On.Delete.Cascade,
)
assert q.get_query() == (
    "CREATE TABLE orders (user_id INTEGER REFERENCES users (id) ON DELETE CASCADE)"
)
```

### Table constraints

Table-level constraints are passed alongside the column defs: `PrimaryKey(...)`, `Unique(...)`, `Check(...)`, `ForeignKey(...).References(...)`, optionally named with `Constraint("name")`:

```python
from sqlinpython import Check, ColumnDef, Constraint, Create, ForeignKey, PrimaryKey, Unique, col

q = Create.Table("t")(
    ColumnDef("a"),
    ColumnDef("b"),
    Constraint("pk").PrimaryKey(col("a")),
    Unique(col("a"), col("b")),
    Check(col("a") > 0),
    ForeignKey("b").References("other"),
)
assert q.get_query() == (
    "CREATE TABLE t ("
    + "a, b, "
    + "CONSTRAINT pk PRIMARY KEY (a), "
    + "UNIQUE (a, b), "
    + "CHECK (a > 0), "
    + "FOREIGN KEY(b) REFERENCES other"
    + ")"
)
```

### CREATE TABLE ... AS SELECT

```python
from sqlinpython import Create, Select

assert (
    Create.Temp.Table("t").As(Select(1)).get_query()
    == "CREATE TEMP TABLE t AS SELECT 1"
)
```

## CREATE INDEX

`Create.Index("name").On("table", ...)` takes indexed columns (expressions, optionally with `Desc` etc.) and an optional partial-index `Where`:

```python
from sqlinpython import Create, col

assert (
    Create.Unique.Index.IfNotExists("my_index").On("my_table", col("col1"), col("col2").Desc).get_query()
    == "CREATE UNIQUE INDEX IF NOT EXISTS my_index ON my_table (col1, col2 DESC)"
)
assert (
    Create.Index("my_index").On("my_table", col("col1")).Where(col("col1") > 0).get_query()
    == "CREATE INDEX my_index ON my_table (col1) WHERE col1 > 0"
)
```

## CREATE VIEW

```python
from sqlinpython import Create, Select

assert (
    Create.View("my_view")("col1", "col2").As(Select(1)).get_query()
    == "CREATE VIEW my_view (col1, col2) AS SELECT 1"
)
```

## CREATE TRIGGER

The trigger event reads like the SQL: optional `Before` / `After` / `InsteadOf`, then `Delete` / `Insert` / `Update` (or `Update.Of(columns)`), then `.On(table)`. Optional `ForEachRow` and `When(...)` precede the `Begin(...)` body, which takes the statements and terminates with `.End`:

```python
from sqlinpython import Create, Insert, Update, col

q = (
    Create.Trigger("audit_users")
    .After.Update.On("users")
    .ForEachRow.When(col("old", "name").ne(col("new", "name")))
    .Begin(
        Insert.Into("audit")("user_id").Values((1,)),
        Update("users").Set(updated=1),
    )
    .End
)
assert q.get_query() == (
    "CREATE TRIGGER audit_users AFTER UPDATE ON users FOR EACH ROW "
    + "WHEN old.name != new.name BEGIN "
    + "INSERT INTO audit (user_id) VALUES (1); "
    + "UPDATE users SET updated = 1; "
    + "END"
)
```

Trigger bodies are where the [`Raise` expression](./expressions.md) is used.

## CREATE VIRTUAL TABLE

The module arguments are passed as raw strings, since their syntax is module-specific:

```python
from sqlinpython import Create

assert (
    Create.VirtualTable("my_vtable").Using("fts5")("content", "tokenize = 'porter'").get_query()
    == "CREATE VIRTUAL TABLE my_vtable USING fts5(content, tokenize = 'porter')"
)
```
