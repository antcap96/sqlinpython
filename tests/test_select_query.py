from sqlinpython.expression import Value
from sqlinpython.select_expression import All, Alias
from sqlinpython.column_def import ColumnRef
from sqlinpython.select import Select, TableSpec
import sqlinpython.functions as f


def test_select_query_1() -> None:
    assert Select(All).From(TableSpec("TEST")).get_query() == "SELECT * FROM TEST"


def test_select_query_2() -> None:
    assert (
        Select.Distinct(Alias(ColumnRef("NAME"))).From(TableSpec("TEST")).get_query()
        == "SELECT DISTINCT NAME FROM TEST"
    )


def test_select_query_3() -> None:
    assert (
        Select(Alias(ColumnRef("ID")), Alias(f.Count(Value(1))))
        .From(TableSpec("TEST"))
        .GroupBy(ColumnRef("ID"))
        .get_query()
        == "SELECT ID, COUNT(1) FROM TEST GROUP BY ID"
    )


def test_select_query_4() -> None:
    assert (
        Select(Alias(ColumnRef("NAME")), Alias(f.Sum(ColumnRef("VAL"))))
        .From(TableSpec("TEST"))
        .GroupBy(ColumnRef("NAME"))
        .Having(f.Count(Value(1)) > (Value(2)))
        .get_query()
        == "SELECT NAME, SUM(VAL) FROM TEST GROUP BY NAME HAVING COUNT(1) > 2"
    )


def test_select_query_5() -> None:
    assert (
        Select(
            Alias(ColumnRef("d", "dept_id")),
            Alias(ColumnRef("e", "dept_id")),
            Alias(ColumnRef("e", "name")),
        )
        .From(
            TableSpec("DEPT d").Join(
                TableSpec("EMPL e"),
                on=ColumnRef("e", "dept_id") == (ColumnRef("d", "dept_id")),
            )
        )
        .get_query()
        == "SELECT d.dept_id, e.dept_id, e.name FROM DEPT d JOIN EMPL e ON e.dept_id = d.dept_id"
    )


def test_select_1() -> None:
    assert (
        Select(All).From(TableSpec("TEST")).Limit(1000).get_query()
        == "SELECT * FROM TEST LIMIT 1000"
    )


def test_select_2() -> None:
    assert (
        Select(All).From(TableSpec("TEST")).Limit(1000).Offset(100).get_query()
        == "SELECT * FROM TEST LIMIT 1000 OFFSET 100"
    )


def test_select_3() -> None:
    assert (
        Select(Alias(ColumnRef("full_name")))
        .From(TableSpec("SALES_PERSON"))
        .Where(ColumnRef("ranking") >= Value(5.0))
        .UnionAll(
            Select(Alias(ColumnRef("reviewer_name")))
            .From(TableSpec("CUSTOMER_REVIEW"))
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
