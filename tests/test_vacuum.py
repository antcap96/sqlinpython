from sqlinpython import Vacuum


def test_vacuum() -> None:
    assert Vacuum.get_query() == "VACUUM"
    assert Vacuum("schema").get_query() == "VACUUM schema"
    assert Vacuum("schema").Into("file").get_query() == "VACUUM schema INTO file"
    assert Vacuum.Into("file").get_query() == "VACUUM INTO file"
