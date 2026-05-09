from sqlinpython import Attach
from sqlinpython import expression as expr
from sqlinpython.name import Name


def test_attach_as_str() -> None:
    q = Attach(expr.literal("file")).As("name")
    assert q.get_query() == 'ATTACH "file" AS name'


def test_attach_as_name() -> None:
    q = Attach(expr.literal("file")).As(Name("name"))
    assert q.get_query() == 'ATTACH "file" AS name'


def test_attach_database_as_str() -> None:
    q = Attach.Database(expr.literal("file")).As("name")
    assert q.get_query() == 'ATTACH DATABASE "file" AS name'


def test_attach_database_as_name() -> None:
    q = Attach.Database(expr.literal("file")).As(Name("name"))
    assert q.get_query() == 'ATTACH DATABASE "file" AS name'
