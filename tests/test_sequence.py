from sqlinpython import CreateSequence, Current, DropSequence, Next, SequenceRef, Value


def test_create_sequence_test_1() -> None:
    assert (
        CreateSequence(SequenceRef("my_sequence"))._create_query()
        == "CREATE SEQUENCE my_sequence"
    )


def test_create_sequence_test_2() -> None:
    assert (
        CreateSequence(SequenceRef("my_sequence"))
        .StartWith(Value(-1000))
        ._create_query()
        == "CREATE SEQUENCE my_sequence START WITH -1000"
    )


def test_create_sequence_test_3() -> None:
    assert (
        CreateSequence(SequenceRef("my_sequence"))
        .IncrementBy(Value(10))
        ._create_query()
        == "CREATE SEQUENCE my_sequence INCREMENT BY 10"
    )


def test_create_sequence_test_4() -> None:
    assert (
        CreateSequence(SequenceRef("my_schema", "my_sequence"))
        .Start(Value(0))
        .Cache(Value(10))
        ._create_query()
        == "CREATE SEQUENCE my_schema.my_sequence START 0 CACHE 10"
    )


def test_sequence_1() -> None:
    assert (
        Next.Value.For(SequenceRef("my_table_id"))._create_query()
        == "NEXT VALUE FOR my_table_id"
    )


def test_sequence_2() -> None:
    assert (
        Next.Values(5).For(SequenceRef("my_table_id"))._create_query()
        == "NEXT 5 VALUES FOR my_table_id"
    )


def test_sequence_3() -> None:
    assert (
        Current.Value.For(SequenceRef("my_schema", "my_id_generator"))._create_query()
        == "CURRENT VALUE FOR my_schema.my_id_generator"
    )


def test_drop_sequence_1() -> None:
    assert (
        DropSequence(SequenceRef("my_sequence")).get_query()
        == "DROP SEQUENCE my_sequence"
    )


def test_drop_sequence_2() -> None:
    assert (
        DropSequence.IfExists(SequenceRef("my_schema", "my_sequence")).get_query()
        == "DROP SEQUENCE IF EXISTS my_schema.my_sequence"
    )
