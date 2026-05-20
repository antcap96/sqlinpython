from sqlinpython import Create, CreateViewStatement, Name, Select, literal


def test_create_view() -> None:
    q = Create.View("my_view").As(Select(literal(1)))
    assert isinstance(q, CreateViewStatement)
    assert q.get_query() == "CREATE VIEW my_view AS SELECT 1"


def test_create_temp_view() -> None:
    q = Create.Temp.View("my_view").As(Select(literal(1)))
    assert isinstance(q, CreateViewStatement)
    assert q.get_query() == "CREATE TEMP VIEW my_view AS SELECT 1"


def test_create_temporary_view() -> None:
    q = Create.Temporary.View("my_view").As(Select(literal(1)))
    assert isinstance(q, CreateViewStatement)
    assert q.get_query() == "CREATE TEMPORARY VIEW my_view AS SELECT 1"


def test_create_if_not_exists_view() -> None:
    q = Create.View.IfNotExists("my_view").As(Select(literal(1)))
    assert isinstance(q, CreateViewStatement)
    assert q.get_query() == "CREATE VIEW IF NOT EXISTS my_view AS SELECT 1"


def test_create_temp_if_not_exists_view() -> None:
    q = Create.Temp.View.IfNotExists("my_view").As(Select(literal(1)))
    assert isinstance(q, CreateViewStatement)
    assert q.get_query() == "CREATE TEMP VIEW IF NOT EXISTS my_view AS SELECT 1"


def test_create_qualified_view() -> None:
    q = Create.View("my_schema", "my_view").As(Select(literal(1)))
    assert isinstance(q, CreateViewStatement)
    assert q.get_query() == "CREATE VIEW my_schema.my_view AS SELECT 1"


def test_create_view_columns() -> None:
    q = Create.View("my_view")("col1", "col2").As(Select(literal(1)))
    assert isinstance(q, CreateViewStatement)
    assert q.get_query() == "CREATE VIEW my_view (col1, col2) AS SELECT 1"


def test_create_view_column_names() -> None:
    q = Create.View(Name("my_view"))(Name("col1"), "col2").As(Select(literal(1)))
    assert isinstance(q, CreateViewStatement)
    assert q.get_query() == "CREATE VIEW my_view (col1, col2) AS SELECT 1"


def test_create_view_columns_not_empty() -> None:
    Create.View(Name("my_view"))()  # type: ignore[call-arg] # pyright: ignore[reportCallIssue]
    # ty doesn't currently identify this error -ty: ignore[missing-argument]
