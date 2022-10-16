import pytest

from sqlinpython import (
    BindParam,
    ColumnName,
    ColumnRef,
    Constrain,
    ConstrainName,
    CreateTable,
    DropTable,
    Name,
    TableOption,
    TableRef,
    Value,
)
from sqlinpython import datatype as dt
from sqlinpython.name import quote_if_necessary


def test_create_table_1() -> None:
    assert (
        CreateTable(TableRef("my_schema", "my_table"))(
            ColumnRef("id")(dt.Bigint).NotNull.PrimaryKey, ColumnRef("date")(dt.Date)
        ).get_query()
        == "CREATE TABLE my_schema.my_table (id BIGINT NOT NULL PRIMARY KEY, date DATE)"
    )


@pytest.mark.xfail(
    reason="this test fails because create table is receiving a column ref"
    " without datatype. Not sure if this is valid..."
)
def test_create_table_2() -> None:
    assert CreateTable(TableRef("my_table"))(
        ColumnRef("id")(dt.Integer).NotNull.PrimaryKey.Desc,
        ColumnRef("date")(dt.Date).NotNull,
        ColumnRef("m", "db_utilization")(dt.Decimal),
        ColumnRef("i", "db_utilization"),  # type: ignore
    )(TableOption("m.DATA_BLOCK_ENCODING='DIFF'")).get_query() == (
        "CREATE TABLE my_table (id INTEGER NOT NULL PRIMARY KEY DESC,"
        " date DATE NOT NULL,"
        " m.db_utilization DECIMAL, i.db_utilization)"
        " m.DATA_BLOCK_ENCODING='DIFF'"
    )


def test_create_table_3() -> None:
    assert CreateTable(TableRef("stats", "prod_metrics"))(
        ColumnRef("host")(dt.Char(50)).NotNull,
        ColumnRef("created_date")(dt.Date).NotNull,
        ColumnRef("txn_count")(dt.Bigint),
        constrain=Constrain(ConstrainName("pk")).PrimaryKey(
            ColumnName("host"), ColumnName("created_date")
        ),
    ).get_query() == (
        "CREATE TABLE stats.prod_metrics (host CHAR(50) NOT NULL,"
        " created_date DATE NOT NULL,"
        " txn_count BIGINT CONSTRAINT pk PRIMARY KEY(host, created_date))"
    )


def test_create_table_4() -> None:
    assert CreateTable.IfNotExists(
        TableRef(Name("my_case_sensitive_table", force_quote=True))
    )(
        ColumnRef(Name("id", force_quote=True))(dt.Char(10)).NotNull.PrimaryKey,
        ColumnRef(Name("value", force_quote=True))(dt.Integer),
    )(
        TableOption("DATA_BLOCK_ENCODING='NONE'"),
        TableOption("VERSIONS=5"),
        TableOption("MAX_FILESIZE=2000000"),
    ).SplitOn(
        BindParam.q, BindParam.q, BindParam.q
    ).get_query() == (
        'CREATE TABLE IF NOT EXISTS "my_case_sensitive_table"'
        ' ("id" CHAR(10) NOT NULL PRIMARY KEY, "value" INTEGER)'
        " DATA_BLOCK_ENCODING='NONE', VERSIONS=5, MAX_FILESIZE=2000000 SPLIT ON(?, ?, ?)"
    )


def test_create_table_5() -> None:
    assert CreateTable.IfNotExists(TableRef("my_schema", "my_table"))(
        ColumnRef("org_id")(dt.Char(15)),
        ColumnRef("entity_id")(dt.Char(15)),
        ColumnRef("payload")(dt.Binary(1000)),
        constrain=Constrain(ConstrainName("pk")).PrimaryKey(
            ColumnName("org_id"), ColumnName("entity_id")
        ),
    )(TableOption("TTL=86400")).get_query() == (
        "CREATE TABLE IF NOT EXISTS my_schema.my_table ("
        "org_id CHAR(15), entity_id CHAR(15), payload BINARY(1000)"
        " CONSTRAINT pk PRIMARY KEY(org_id, entity_id))"
        " TTL=86400"
    )


def test_create_table_6() -> None:
    assert CreateTable.IfNotExists(
        TableRef(Name("my_case_sensitive_table", force_quote=True))
    )(ColumnRef(Name("id", force_quote=True))(dt.Char(10))).SplitOn(
        Value(1), BindParam.Index(2), Value("val")
    ).get_query() == (
        'CREATE TABLE IF NOT EXISTS "my_case_sensitive_table"'
        ' ("id" CHAR(10))'
        " SPLIT ON(1, :2, 'val')"
    )


def test_drop_table_1() -> None:
    assert (
        DropTable(TableRef("my_schema", "my_table")).get_query()
        == "DROP TABLE my_schema.my_table"
    )


def test_drop_table_2() -> None:
    assert (
        DropTable.IfExists(TableRef("my_table")).get_query()
        == "DROP TABLE IF EXISTS my_table"
    )


def test_drop_table_3() -> None:
    assert (
        DropTable(TableRef("my_schema", "my_table")).Cascade.get_query()
        == "DROP TABLE my_schema.my_table CASCADE"
    )


def test_quote_if_necessary() -> None:
    assert quote_if_necessary("") == '""'
    assert quote_if_necessary("abc") == "abc"
    assert quote_if_necessary("a1") == "a1"
    assert quote_if_necessary("a.c") == '"a.c"'
    assert quote_if_necessary("ã") == '"ã"'
    assert quote_if_necessary("10") == '"10"'
    assert quote_if_necessary("_10") == "_10"
    assert quote_if_necessary("aAa") == "aAa"
    assert quote_if_necessary('a"2"1') == '"a""2""1"'
