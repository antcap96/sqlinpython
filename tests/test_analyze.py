from sqlinpython import Analyze, Name


def test_analyze() -> None:
    q = Analyze("name")
    assert q.get_query() == "ANALYZE name"


def test_analyze_name() -> None:
    q = Analyze(Name("name"))
    assert q.get_query() == "ANALYZE name"


def test_qualified_analyze() -> None:
    q = Analyze("schema", "name")
    assert q.get_query() == "ANALYZE schema.name"


def test_qualified_analyze_name() -> None:
    q = Analyze(Name("schema"), Name("name"))
    assert q.get_query() == "ANALYZE schema.name"


def test_analyze_no_args() -> None:
    assert Analyze.get_query() == "ANALYZE"
