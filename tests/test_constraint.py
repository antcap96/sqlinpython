from sqlinpython.name import constrain, ConstrainName, Column


def test_constrain_1() -> None:
    assert constrain(ConstrainName("my_pk")).PrimaryKey(
        Column("host"), Column("created_date")
    ).get_query() == ("CONSTRAINT my_pk PRIMARY KEY(host, created_date)")


def test_constrain_2() -> None:
    assert constrain(ConstrainName("my_pk")).PrimaryKey(
        Column("host").Asc, Column("created_date").Desc
    ).get_query() == ("CONSTRAINT my_pk PRIMARY KEY(host ASC, created_date DESC)")


def test_constrain_3() -> None:
    assert constrain(ConstrainName("my_pk")).PrimaryKey(
        Column("host").Asc, Column("created_date").Desc.RowTimestamp
    ).get_query() == (
        "CONSTRAINT my_pk PRIMARY KEY(host ASC, created_date DESC ROW_TIMESTAMP)"
    )
