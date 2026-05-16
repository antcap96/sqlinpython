from sqlinpython import ColumnName, Create, literal


def test_create_index() -> None:
    col1 = ColumnName("col1")
    col2 = ColumnName("col2")

    assert (
        Create.Index("my_index").On("my_table", col1).get_query()
        == "CREATE INDEX my_index ON my_table (col1)"
    )
    assert (
        Create.Index("my_schema", "my_index").On("my_table", col1).get_query()
        == "CREATE INDEX my_schema.my_index ON my_table (col1)"
    )
    assert (
        Create.Unique.Index("my_index").On("my_table", col1).get_query()
        == "CREATE UNIQUE INDEX my_index ON my_table (col1)"
    )
    assert (
        Create.Index.IfNotExists("my_index").On("my_table", col1).get_query()
        == "CREATE INDEX IF NOT EXISTS my_index ON my_table (col1)"
    )
    assert (
        Create.Unique.Index.IfNotExists("my_index")
        .On("my_table", col1, col2.Desc)
        .get_query()
        == "CREATE UNIQUE INDEX IF NOT EXISTS my_index ON my_table (col1, col2 DESC)"
    )
    assert (
        Create.Index("my_index")
        .On("my_table", col1)
        .Where(literal(1) > literal(0))
        .get_query()
        == "CREATE INDEX my_index ON my_table (col1) WHERE 1 > 0"
    )
    assert (
        Create.Index("main", "my_index").On("my_table", col1).get_query()
        == "CREATE INDEX main.my_index ON my_table (col1)"
    )
