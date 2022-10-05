from sqlinpython import Cast, ColumnRef
from sqlinpython import datatype as dt


def test_cast_1() -> None:
    assert (
        Cast(ColumnRef("my_int"), _as=dt.Decimal)._create_query()
        == "CAST (my_int AS DECIMAL)"
    )


def test_cast_2() -> None:
    assert (
        Cast(ColumnRef("my_timestamp"), _as=dt.Date)._create_query()
        == "CAST (my_timestamp AS DATE)"
    )
