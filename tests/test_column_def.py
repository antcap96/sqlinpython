from sqlinpython.column_def import ColumnRef
from sqlinpython.datatype import *


def test_column_def_1() -> None:
    assert (
        ColumnRef("id")(Char(15)).NotNull.PrimaryKey.get_query()
        == "id CHAR(15) NOT NULL PRIMARY KEY"
    )


def test_column_def_2() -> None:
    assert ColumnRef("key")(Integer).Null.get_query() == "key INTEGER NULL"


def test_column_def_3() -> None:
    assert (
        ColumnRef("m", "response_time")(Bigint).get_query() == "m.response_time BIGINT"
    )


def test_column_def_4() -> None:
    assert (
        ColumnRef("created_date")(Date).NotNull.PrimaryKey.RowTimestamp.get_query()
        == "created_date DATE NOT NULL PRIMARY KEY ROW_TIMESTAMP"
    )
