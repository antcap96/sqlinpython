# Other statements

## ALTER TABLE

`AlterTable` (imported from the top level) covers renames, column add/drop, and the ALTER COLUMN forms:

```python
from sqlinpython import AlterTable, ColumnDef, TypeName

assert AlterTable("t").Rename.To("t2").get_query() == "ALTER TABLE t RENAME TO t2"
assert (
    AlterTable("t").Rename.Column("c").To("c2").get_query()
    == "ALTER TABLE t RENAME COLUMN c TO c2"
)
assert (
    AlterTable("t").Add.Column(ColumnDef("c")(TypeName("INT"))).get_query()
    == "ALTER TABLE t ADD COLUMN c INT"
)
assert AlterTable("t").Drop.Column("c").get_query() == "ALTER TABLE t DROP COLUMN c"
assert AlterTable("t").Alter("c").SetNotNull.get_query() == "ALTER TABLE t ALTER c SET NOT NULL"
```

## DROP

```python
from sqlinpython import Drop

assert Drop.Table("name").get_query() == "DROP TABLE name"
assert Drop.Index("name").get_query() == "DROP INDEX name"
assert Drop.View("name").get_query() == "DROP VIEW name"
assert Drop.Trigger("name").get_query() == "DROP TRIGGER name"
assert Drop.Table.IfExists("a", "b").get_query() == "DROP TABLE IF EXISTS a.b"
```

## Transactions and savepoints

The transaction entry points are complete statements by themselves; optional keywords chain as properties:

```python
from sqlinpython import Begin, Commit, End, Release, Rollback, Savepoint

assert Begin.get_query() == "BEGIN"
assert Begin.Immediate.Transaction.get_query() == "BEGIN IMMEDIATE TRANSACTION"
assert Commit.get_query() == "COMMIT"
assert End.Transaction.get_query() == "END TRANSACTION"

assert Savepoint("a").get_query() == "SAVEPOINT a"
assert Release("a").get_query() == "RELEASE a"
assert Rollback.get_query() == "ROLLBACK"
assert Rollback.To.Savepoint("a").get_query() == "ROLLBACK TO SAVEPOINT a"
```

## PRAGMA

A `Pragma` can be read bare, or given a value in either the `=` or the call form (`eq=True` selects `=`):

```python
from sqlinpython import Pragma

assert Pragma("name").get_query() == "PRAGMA name"
assert Pragma("schema", "name").get_query() == "PRAGMA schema.name"
assert Pragma("name")(42).get_query() == "PRAGMA name (42)"
assert Pragma("name")(42, eq=True).get_query() == "PRAGMA name = 42"
```

## ANALYZE, REINDEX, VACUUM

```python
from sqlinpython import Analyze, Reindex, Vacuum

assert Analyze.get_query() == "ANALYZE"
assert Analyze("schema", "name").get_query() == "ANALYZE schema.name"
assert Reindex.get_query() == "REINDEX"
assert (
    Reindex.Schema("schema_name", "table_or_index_name").get_query()
    == "REINDEX schema_name.table_or_index_name"
)
assert Vacuum.get_query() == "VACUUM"
assert Vacuum("schema").Into("file").get_query() == "VACUUM schema INTO file"
```

## ATTACH and DETACH

```python
from sqlinpython import Attach, Detach

assert Attach("file").As("name").get_query() == "ATTACH 'file' AS name"
assert Detach("name").get_query() == "DETACH name"
```

## EXPLAIN

`Explain` wraps any complete statement — except another `EXPLAIN`, which the type checkers reject:

```python
from sqlinpython import Explain, Select

assert Explain(Select(1)).get_query() == "EXPLAIN SELECT 1"
assert Explain.QueryPlan(Select(1)).get_query() == "EXPLAIN QUERY PLAN SELECT 1"
```
