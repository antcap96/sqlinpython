from sqlinpython import DropTable


def test_drop_table_basic() -> None:
    assert DropTable("a").get_query() == "DROP TABLE a"


def test_drop_table_schema_qualified() -> None:
    assert DropTable("a", "b").get_query() == "DROP TABLE a.b"


def test_drop_table_quoted_name() -> None:
    assert DropTable("a", 'b"').get_query() == 'DROP TABLE a."b"""'


def test_drop_table_if_exists_basic() -> None:
    assert DropTable.IfExists("a").get_query() == "DROP TABLE IF EXISTS a"


def test_drop_table_if_exists_schema_qualified() -> None:
    assert DropTable.IfExists("a", "b").get_query() == "DROP TABLE IF EXISTS a.b"


def test_drop_table_if_exists_quoted_name() -> None:
    assert DropTable.IfExists("a", 'b"').get_query() == 'DROP TABLE IF EXISTS a."b"""'
