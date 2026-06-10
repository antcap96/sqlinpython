import pytest

from sqlinpython import ColumnName, Create, literal

col1 = ColumnName("col1")
col2 = ColumnName("col2")


def test_create_index_basic() -> None:
    assert (
        Create.Index("my_index").On("my_table", col1).get_query()
        == "CREATE INDEX my_index ON my_table (col1)"
    )


def test_create_index_schema_qualified() -> None:
    assert (
        Create.Index("my_schema", "my_index").On("my_table", col1).get_query()
        == "CREATE INDEX my_schema.my_index ON my_table (col1)"
    )


def test_create_unique_index() -> None:
    assert (
        Create.Unique.Index("my_index").On("my_table", col1).get_query()
        == "CREATE UNIQUE INDEX my_index ON my_table (col1)"
    )


def test_create_index_if_not_exists() -> None:
    assert (
        Create.Index.IfNotExists("my_index").On("my_table", col1).get_query()
        == "CREATE INDEX IF NOT EXISTS my_index ON my_table (col1)"
    )


def test_create_unique_index_if_not_exists_multi_column() -> None:
    assert (
        Create.Unique.Index.IfNotExists("my_index")
        .On("my_table", col1, col2.Desc)
        .get_query()
        == "CREATE UNIQUE INDEX IF NOT EXISTS my_index ON my_table (col1, col2 DESC)"
    )


def test_create_index_where() -> None:
    assert (
        Create.Index("my_index")
        .On("my_table", col1)
        .Where(literal(1) > literal(0))
        .get_query()
        == "CREATE INDEX my_index ON my_table (col1) WHERE 1 > 0"
    )


def test_create_index_main_schema() -> None:
    assert (
        Create.Index("main", "my_index").On("my_table", col1).get_query()
        == "CREATE INDEX main.my_index ON my_table (col1)"
    )


def test_create_index_where_accepts_python_literal() -> None:
    assert (
        Create.Index("my_index").On("my_table", col1).Where(1).get_query()
        == "CREATE INDEX my_index ON my_table (col1) WHERE 1"
    )


def test_create_index_if_not_exists_rejects_on_without_name() -> None:
    # .On() must not be accessible before providing an index name
    with pytest.raises(AttributeError):
        Create.Index.IfNotExists.On("my_table", col1)  # type: ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType] # ty: ignore[unresolved-attribute]
