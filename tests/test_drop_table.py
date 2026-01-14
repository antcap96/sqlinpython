from sqlinpython import DropTable


def test_create_table() -> None:
    assert DropTable("a").get_query() == "DROP TABLE a"
    assert DropTable("a", "b").get_query() == "DROP TABLE a.b"
    assert DropTable("a", 'b"').get_query() == 'DROP TABLE a."b"""'


def test_create_table_if_exists() -> None:
    assert DropTable.IfExists("a").get_query() == "DROP TABLE IF EXISTS a"
    assert DropTable.IfExists("a", "b").get_query() == "DROP TABLE IF EXISTS a.b"
    assert DropTable.IfExists("a", 'b"').get_query() == 'DROP TABLE IF EXISTS a."b"""'
