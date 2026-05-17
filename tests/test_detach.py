from sqlinpython import Detach, DetachStatement, Name


def test_detach() -> None:
    q = Detach("name")
    assert isinstance(q, DetachStatement)
    assert q.get_query() == "DETACH name"


def test_detach_name() -> None:
    q = Detach(Name("name"))
    assert isinstance(q, DetachStatement)
    assert q.get_query() == "DETACH name"


def test_detach_database() -> None:
    q = Detach.Database("name")
    assert isinstance(q, DetachStatement)
    assert q.get_query() == "DETACH DATABASE name"


def test_detach_database_name() -> None:
    q = Detach.Database(Name("name"))
    assert isinstance(q, DetachStatement)
    assert q.get_query() == "DETACH DATABASE name"
