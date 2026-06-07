from sqlinpython import Attach, Name, literal


def test_attach_as_str() -> None:
    q = Attach(literal("file")).As("name")
    assert q.get_query() == "ATTACH 'file' AS name"


def test_attach_as_name() -> None:
    q = Attach(literal("file")).As(Name("name"))
    assert q.get_query() == "ATTACH 'file' AS name"


def test_attach_database_as_str() -> None:
    q = Attach.Database(literal("file")).As("name")
    assert q.get_query() == "ATTACH DATABASE 'file' AS name"


def test_attach_database_as_name() -> None:
    q = Attach.Database(literal("file")).As(Name("name"))
    assert q.get_query() == "ATTACH DATABASE 'file' AS name"


def test_attach_accepts_python_literal() -> None:
    q = Attach("file").As("name")
    assert q.get_query() == "ATTACH 'file' AS name"
