from sqlinpython.name import Constrain, ConstrainName, ColumnNameConstrainAscDesc


def test1() -> None:
    constrain = Constrain()
    column = ColumnNameConstrainAscDesc
    assert (
        constrain(ConstrainName("test")).PrimaryKey(column("col1")).get_query()
        == "CONSTRAIN test PRIMARY KEY(col1)"
    )
