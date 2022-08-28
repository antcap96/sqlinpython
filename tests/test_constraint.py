from sqlinpython import ColumnName, Constrain, ConstrainName


def test_constrain_1() -> None:
    assert Constrain(ConstrainName("my_pk")).PrimaryKey(
        ColumnName("host"), ColumnName("created_date")
    )._create_query() == ("CONSTRAINT my_pk PRIMARY KEY(host, created_date)")


def test_constrain_2() -> None:
    assert Constrain(ConstrainName("my_pk")).PrimaryKey(
        ColumnName("host").Asc, ColumnName("created_date").Desc
    )._create_query() == ("CONSTRAINT my_pk PRIMARY KEY(host ASC, created_date DESC)")


def test_constrain_3() -> None:
    assert Constrain(ConstrainName("my_pk")).PrimaryKey(
        ColumnName("host").Asc, ColumnName("created_date").Desc.RowTimestamp
    )._create_query() == (
        "CONSTRAINT my_pk PRIMARY KEY(host ASC, created_date DESC ROW_TIMESTAMP)"
    )
