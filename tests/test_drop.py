from typing import assert_type

from sqlinpython import Drop
from sqlinpython.types import (
    DropIndexStatement,
    DropTableStatement,
    DropTriggerStatement,
    DropViewStatement,
)


def test_drop_table() -> None:
    q = Drop.Table("name")
    _ = assert_type(q, DropTableStatement)
    assert q.get_query() == "DROP TABLE name"


def test_drop_view() -> None:
    q = Drop.View("name")
    _ = assert_type(q, DropViewStatement)
    assert q.get_query() == "DROP VIEW name"


def test_drop_trigger() -> None:
    q = Drop.Trigger("name")
    _ = assert_type(q, DropTriggerStatement)
    assert q.get_query() == "DROP TRIGGER name"


def test_drop_index() -> None:
    q = Drop.Index("name")
    _ = assert_type(q, DropIndexStatement)
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
