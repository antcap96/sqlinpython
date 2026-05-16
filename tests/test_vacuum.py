from sqlinpython import Vacuum


def test_vacuum_no_args() -> None:
    assert Vacuum.get_query() == "VACUUM"


def test_vacuum_schema() -> None:
    assert Vacuum("schema").get_query() == "VACUUM schema"


def test_vacuum_schema_into() -> None:
    assert Vacuum("schema").Into("file").get_query() == "VACUUM schema INTO file"


def test_vacuum_into() -> None:
    assert Vacuum.Into("file").get_query() == "VACUUM INTO file"
