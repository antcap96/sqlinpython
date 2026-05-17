from sqlinpython import Name, Reindex, ReindexStatement


def test_reindex() -> None:
    assert isinstance(Reindex, ReindexStatement)
    assert Reindex.get_query() == "REINDEX"


def test_reindex_collation() -> None:
    q = Reindex("collation_name")
    assert isinstance(q, ReindexStatement)
    assert q.get_query() == "REINDEX collation_name"


def test_reindex_collation_name() -> None:
    q = Reindex(Name("collation_name"))
    assert isinstance(q, ReindexStatement)
    assert q.get_query() == "REINDEX collation_name"


def test_reindex_expressions() -> None:
    q = Reindex.Expressions
    assert isinstance(q, ReindexStatement)
    assert q.get_query() == "REINDEX EXPRESSIONS"


def test_reindex_schema_str() -> None:
    q = Reindex.Schema("schema_name", "table_or_index_name")
    assert isinstance(q, ReindexStatement)
    assert q.get_query() == "REINDEX schema_name.table_or_index_name"


def test_reindex_schema_name() -> None:
    q = Reindex.Schema("schema_name", Name("table_or_index_name"))
    assert isinstance(q, ReindexStatement)
    assert q.get_query() == "REINDEX schema_name.table_or_index_name"
