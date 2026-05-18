from sqlinpython import Name, Pragma, PragmaStatement


def test_pragma() -> None:
    q = Pragma("name")
    assert isinstance(q, PragmaStatement)
    assert q.get_query() == "PRAGMA name"


def test_pragma_name() -> None:
    q = Pragma(Name("name"))
    assert isinstance(q, PragmaStatement)
    assert q.get_query() == "PRAGMA name"


def test_pragma_schema() -> None:
    q = Pragma("schema", "name")
    assert isinstance(q, PragmaStatement)
    assert q.get_query() == "PRAGMA schema.name"


def test_pragma_bool() -> None:
    q = Pragma("name")(True)
    assert isinstance(q, PragmaStatement)
    assert q.get_query() == "PRAGMA name (true)"


def test_pragma_bool_false() -> None:
    q = Pragma("name")(False)
    assert isinstance(q, PragmaStatement)
    assert q.get_query() == "PRAGMA name (false)"


def test_pragma_int() -> None:
    q = Pragma("name")(42)
    assert isinstance(q, PragmaStatement)
    assert q.get_query() == "PRAGMA name (42)"


def test_pragma_str() -> None:
    q = Pragma("name")("ok")
    assert isinstance(q, PragmaStatement)
    assert q.get_query() == "PRAGMA name (ok)"


def test_pragma_bool_eq() -> None:
    q = Pragma("name")(True, eq=True)
    assert isinstance(q, PragmaStatement)
    assert q.get_query() == "PRAGMA name = true"


def test_pragma_int_eq() -> None:
    q = Pragma("name")(42, eq=True)
    assert isinstance(q, PragmaStatement)
    assert q.get_query() == "PRAGMA name = 42"


def test_pragma_eq() -> None:
    q = Pragma("name")("ok", eq=True)
    assert isinstance(q, PragmaStatement)
    assert q.get_query() == "PRAGMA name = ok"


def test_pragma_schema_value() -> None:
    q = Pragma("schema", "name")("ok")
    assert isinstance(q, PragmaStatement)
    assert q.get_query() == "PRAGMA schema.name (ok)"


def test_pragma_schema_eq() -> None:
    q = Pragma("schema", "name")("ok", eq=True)
    assert isinstance(q, PragmaStatement)
    assert q.get_query() == "PRAGMA schema.name = ok"


def test_pragma_force_quote() -> None:
    q = Pragma("name")(Name("ok", force_quote=True))
    assert isinstance(q, PragmaStatement)
    assert q.get_query() == 'PRAGMA name ("ok")'
