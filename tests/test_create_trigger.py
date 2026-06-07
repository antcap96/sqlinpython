from sqlinpython import (
    Create,
    CreateTriggerStatement,
    Delete,
    Insert,
    Name,
    Select,
    Update,
    literal,
)


def test_create_trigger_basic() -> None:
    q = (
        Create.Trigger("my_trigger")
        .Delete.On("my_table")
        .Begin(Delete.From("my_table"))
        .End
    )
    assert isinstance(q, CreateTriggerStatement)
    assert (
        q.get_query()
        == "CREATE TRIGGER my_trigger DELETE ON my_table BEGIN DELETE FROM my_table; END"
    )


def test_create_temp_trigger() -> None:
    assert (
        Create.Temp.Trigger("my_trigger")
        .Delete.On("my_table")
        .Begin(Delete.From("my_table"))
        .End.get_query()
        == "CREATE TEMP TRIGGER my_trigger DELETE ON my_table BEGIN DELETE FROM my_table; END"
    )


def test_create_temporary_trigger() -> None:
    assert (
        Create.Temporary.Trigger("my_trigger")
        .Delete.On("my_table")
        .Begin(Delete.From("my_table"))
        .End.get_query()
        == "CREATE TEMPORARY TRIGGER my_trigger DELETE ON my_table BEGIN DELETE FROM my_table; END"
    )


def test_create_trigger_if_not_exists() -> None:
    assert (
        Create.Trigger.IfNotExists("my_trigger")
        .Delete.On("my_table")
        .Begin(Delete.From("my_table"))
        .End.get_query()
        == "CREATE TRIGGER IF NOT EXISTS my_trigger DELETE ON my_table BEGIN DELETE FROM my_table; END"
    )


def test_create_trigger_qualified_name() -> None:
    assert (
        Create.Trigger("main", "my_trigger")
        .Delete.On("my_table")
        .Begin(Delete.From("my_table"))
        .End.get_query()
        == "CREATE TRIGGER main.my_trigger DELETE ON my_table BEGIN DELETE FROM my_table; END"
    )


def test_create_trigger_before_delete() -> None:
    assert (
        Create.Trigger("my_trigger")
        .Before.Delete.On("my_table")
        .Begin(Delete.From("my_table"))
        .End.get_query()
        == "CREATE TRIGGER my_trigger BEFORE DELETE ON my_table BEGIN DELETE FROM my_table; END"
    )


def test_create_trigger_after_insert() -> None:
    assert (
        Create.Trigger("my_trigger")
        .After.Insert.On("my_table")
        .Begin(Delete.From("my_table"))
        .End.get_query()
        == "CREATE TRIGGER my_trigger AFTER INSERT ON my_table BEGIN DELETE FROM my_table; END"
    )


def test_create_trigger_instead_of_update() -> None:
    assert (
        Create.Trigger("my_trigger")
        .InsteadOf.Update.On("my_view")
        .Begin(Delete.From("my_table"))
        .End.get_query()
        == "CREATE TRIGGER my_trigger INSTEAD OF UPDATE ON my_view BEGIN DELETE FROM my_table; END"
    )


def test_create_trigger_update_of() -> None:
    assert (
        Create.Trigger("my_trigger")
        .Update.Of(Name("col1"), Name("col2"))
        .On("my_table")
        .Begin(Delete.From("my_table"))
        .End.get_query()
        == "CREATE TRIGGER my_trigger UPDATE OF col1, col2 ON my_table BEGIN DELETE FROM my_table; END"
    )


def test_create_trigger_update_of_no_args() -> None:
    Create.Trigger("t").Before.Update.Of()  # type: ignore[call-arg] # pyright: ignore[reportCallIssue]
    # ty doesn't currently identify this error -ty: ignore[missing-argument]


def test_create_trigger_for_each_row() -> None:
    assert (
        Create.Trigger("my_trigger")
        .Before.Delete.On("my_table")
        .ForEachRow.Begin(Delete.From("my_table"))
        .End.get_query()
        == "CREATE TRIGGER my_trigger BEFORE DELETE ON my_table FOR EACH ROW BEGIN DELETE FROM my_table; END"
    )


def test_create_trigger_when() -> None:
    assert (
        Create.Trigger("my_trigger")
        .Before.Delete.On("my_table")
        .When(literal(1))
        .Begin(Delete.From("my_table"))
        .End.get_query()
        == "CREATE TRIGGER my_trigger BEFORE DELETE ON my_table WHEN 1 BEGIN DELETE FROM my_table; END"
    )


def test_create_trigger_for_each_row_when() -> None:
    assert (
        Create.Trigger("my_trigger")
        .Before.Delete.On("my_table")
        .ForEachRow.When(literal(1))
        .Begin(Delete.From("my_table"))
        .End.get_query()
        == "CREATE TRIGGER my_trigger BEFORE DELETE ON my_table FOR EACH ROW WHEN 1 BEGIN DELETE FROM my_table; END"
    )


def test_create_trigger_when_accepts_python_literal() -> None:
    assert (
        Create.Trigger("my_trigger")
        .Before.Delete.On("my_table")
        .When(1)
        .Begin(Delete.From("my_table"))
        .End.get_query()
        == "CREATE TRIGGER my_trigger BEFORE DELETE ON my_table WHEN 1 BEGIN DELETE FROM my_table; END"
    )


def test_create_trigger_multiple_stmts() -> None:
    assert (
        Create.Trigger("my_trigger")
        .Before.Delete.On("my_table")
        .Begin(Delete.From("my_table"), Delete.From("other_table"))
        .End.get_query()
        == "CREATE TRIGGER my_trigger BEFORE DELETE ON my_table BEGIN DELETE FROM my_table; DELETE FROM other_table; END"
    )


def test_create_trigger_body_statement_types() -> None:
    assert Create.Trigger("my_trigger").Before.Delete.On("my_table").Begin(
        Delete.From("t"),
        Insert.Into("t")("c").Values((literal(1),)),
        Update("t").Set(c=literal(2)),
        Select(literal(3)),
    ).End.get_query() == (
        "CREATE TRIGGER my_trigger BEFORE DELETE ON my_table BEGIN "
        + "DELETE FROM t; "
        + "INSERT INTO t (c) VALUES (1); "
        + "UPDATE t SET c = 2; "
        + "SELECT 3; "
        + "END"
    )


def test_create_temp_if_not_exists_qualified_trigger() -> None:
    assert (
        Create.Temp.Trigger.IfNotExists("main", "my_trigger")
        .Before.Delete.On("my_table")
        .Begin(Delete.From("my_table"))
        .End.get_query()
        == "CREATE TEMP TRIGGER IF NOT EXISTS main.my_trigger BEFORE DELETE ON my_table BEGIN DELETE FROM my_table; END"
    )
