import sqlinpython.functions as f
from sqlinpython import ColumnRef, Select, Star, TableRef, Value
from sqlinpython.datatype import Varchar


def test_select_query_1() -> None:
    assert Select(Star).From(TableRef("TEST")).get_query() == "SELECT * FROM TEST"


def test_select_query_2() -> None:
    assert (
        Select.Distinct(ColumnRef("NAME")).From(TableRef("TEST")).get_query()
        == "SELECT DISTINCT NAME FROM TEST"
    )


def test_select_query_3() -> None:
    assert (
        Select(ColumnRef("ID"), f.Count(Value(1)))
        .From(TableRef("TEST"))
        .GroupBy(ColumnRef("ID"))
        .get_query()
        == "SELECT ID, COUNT(1) FROM TEST GROUP BY ID"
    )


def test_select_query_4() -> None:
    assert (
        Select(ColumnRef("NAME"), f.Sum(ColumnRef("VAL")))
        .From(TableRef("TEST"))
        .GroupBy(ColumnRef("NAME"))
        .Having(f.Count(Value(1)) > (Value(2)))
        .get_query()
        == "SELECT NAME, SUM(VAL) FROM TEST GROUP BY NAME HAVING COUNT(1) > 2"
    )


def test_select_query_5() -> None:
    assert (
        Select(
            ColumnRef("d", "dept_id"),
            ColumnRef("e", "dept_id"),
            ColumnRef("e", "name"),
        )
        .From(
            TableRef("DEPT")
            .As("d", explicit_as=False)
            .Join(
                TableRef("EMPL").As("e", explicit_as=False),
                on=ColumnRef("e", "dept_id") == (ColumnRef("d", "dept_id")),
            )
        )
        .get_query()
        == "SELECT d.dept_id, e.dept_id, e.name "
        "FROM DEPT d JOIN EMPL e ON e.dept_id = d.dept_id"
    )


def test_select_1() -> None:
    assert (
        Select(Star).From(TableRef("TEST")).Limit(1000).get_query()
        == "SELECT * FROM TEST LIMIT 1000"
    )


def test_select_2() -> None:
    assert (
        Select(Star).From(TableRef("TEST")).Limit(1000).Offset(100).get_query()
        == "SELECT * FROM TEST LIMIT 1000 OFFSET 100"
    )


def test_select_3() -> None:
    assert (
        Select(ColumnRef("full_name"))
        .From(TableRef("SALES_PERSON"))
        .Where(ColumnRef("ranking") >= Value(5.0))
        .UnionAll(
            Select(ColumnRef("reviewer_name"))
            .From(TableRef("CUSTOMER_REVIEW"))
            .Where(ColumnRef("score") >= Value(8.0))
        )
        .get_query()
        == "SELECT full_name"
        " FROM SALES_PERSON"
        " WHERE ranking >= 5.0"
        " UNION ALL SELECT reviewer_name"
        " FROM CUSTOMER_REVIEW"
        " WHERE score >= 8.0"
    )


def test_select_recursive_1() -> None:
    assert (
        Select(ColumnRef("a"))
        .From(Select(Star).From(TableRef("test")).Parentheses)
        .get_query()
        == "SELECT a FROM (SELECT * FROM test)"
    )


def test_select_recursive_2() -> None:
    assert (
        Select(ColumnRef("b", "a"))
        .From(Select(Star).From(TableRef("test")).As("b"))
        .get_query()
        == "SELECT b.a FROM (SELECT * FROM test) AS b"
    )


def test_table_spec_1() -> None:
    assert (
        TableRef("PRODUCT_METRICS").As("PM")._create_query() == "PRODUCT_METRICS AS PM"
    )


def test_table_spec_2() -> None:
    assert (
        TableRef("PRODUCT_METRICS")(ColumnRef("referrer")(Varchar))._create_query()
        == "PRODUCT_METRICS(referrer VARCHAR)"
    )


def test_table_spec_3() -> None:
    assert (
        Select(ColumnRef("feature"))
        .From(TableRef("PRODUCT_METRICS"))
        .As("PM")
        ._create_query()
        == "(SELECT feature FROM PRODUCT_METRICS) AS PM"
    )


# table spec tests
# PRODUCT_METRICS(referrer VARCHAR)
# ( SELECT feature FROM PRODUCT_METRICS ) AS PM
