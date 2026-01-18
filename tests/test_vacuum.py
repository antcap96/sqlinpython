from sqlinpython import Vacuum


def test_vacuum():
    assert Vacuum._create_query() == "VACUUM"
    assert Vacuum("schema")._create_query() == "VACUUM schema"
    assert Vacuum("schema").Into("file")._create_query() == "VACUUM schema INTO file"
    assert Vacuum.Into("file")._create_query() == "VACUUM INTO file"
