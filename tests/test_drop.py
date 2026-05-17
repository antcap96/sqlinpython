from sqlinpython import (
    Drop,
    DropIndexStatement,
    DropTableStatement,
    DropTriggerStatement,
    DropViewStatement,
)


def typecheck_isinstance[T](_obj: T, _cls: type[T]) -> None:
    pass


def test_drop_table() -> None:
    q = Drop.Table("name")
    typecheck_isinstance(q, DropTableStatement)
    assert q.get_query() == "DROP TABLE name"


def test_drop_view() -> None:
    q = Drop.View("name")
    typecheck_isinstance(q, DropViewStatement)
    assert q.get_query() == "DROP VIEW name"


def test_drop_trigger() -> None:
    q = Drop.Trigger("name")
    typecheck_isinstance(q, DropTriggerStatement)
    assert q.get_query() == "DROP TRIGGER name"


def test_drop_index() -> None:
    q = Drop.Index("name")
    typecheck_isinstance(q, DropIndexStatement)
    assert q.get_query() == "DROP INDEX name"


def test_drop_table_schema_qualified() -> None:
    assert Drop.Table("a", "b").get_query() == "DROP TABLE a.b"


def test_drop_table_quoted_name() -> None:
    assert Drop.Table("a", 'b"').get_query() == 'DROP TABLE a."b"""'


def test_drop_table_if_exists() -> None:
    assert Drop.Table.IfExists("a").get_query() == "DROP TABLE IF EXISTS a"


def test_drop_table_if_exists_schema_qualified() -> None:
    assert Drop.Table.IfExists("a", "b").get_query() == "DROP TABLE IF EXISTS a.b"


def test_drop_table_if_exists_quoted_name() -> None:
    assert Drop.Table.IfExists("a", 'b"').get_query() == 'DROP TABLE IF EXISTS a."b"""'
