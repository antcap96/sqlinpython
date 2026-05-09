from sqlinpython import AlterTable, ColumnName, TypeName
from sqlinpython import expression as expr


def test_rename_to() -> None:
    q = AlterTable("t").Rename.To("t2")
    assert q.get_query() == "ALTER TABLE t RENAME TO t2"


def test_qualified_table_rename_to() -> None:
    q = AlterTable("s", "t").Rename.To("s2")
    assert q.get_query() == "ALTER TABLE s.t RENAME TO s2"


def test_rename_column1() -> None:
    q = AlterTable("t").Rename.Column("c").To("c2")
    assert q.get_query() == "ALTER TABLE t RENAME COLUMN c TO c2"


def test_rename_column2() -> None:
    q = AlterTable("t").Rename("c").To("c2")
    assert q.get_query() == "ALTER TABLE t RENAME c TO c2"


def test_add_column1() -> None:
    q = AlterTable("t").Add.Column(ColumnName("c")(TypeName("INT")))
    assert q.get_query() == "ALTER TABLE t ADD COLUMN c INT"


def test_add_column2() -> None:
    q = AlterTable("t").Add(ColumnName("c")(TypeName("INT")))
    assert q.get_query() == "ALTER TABLE t ADD c INT"


def test_add_constraint1() -> None:
    q = AlterTable("t").Add.Constraint("x").Check(expr.literal(1))
    assert q.get_query() == "ALTER TABLE t ADD CONSTRAINT x CHECK (1)"


def test_add_constraint2() -> None:
    q = AlterTable("t").Add.Check(expr.literal(1)).OnConflict.Abort
    assert q.get_query() == "ALTER TABLE t ADD CHECK (1) ON CONFLICT ABORT"


def test_drop_column1() -> None:
    q = AlterTable("t").Drop("c")
    assert q.get_query() == "ALTER TABLE t DROP c"


def test_drop_column2() -> None:
    q = AlterTable("t").Drop.Column("c")
    assert q.get_query() == "ALTER TABLE t DROP COLUMN c"


def test_drop_constraint() -> None:
    q = AlterTable("t").Drop.Constraint("x")
    assert q.get_query() == "ALTER TABLE t DROP CONSTRAINT x"


def test_alter_column_set1() -> None:
    q = AlterTable("t").Alter("c").SetNotNull
    assert q.get_query() == "ALTER TABLE t ALTER c SET NOT NULL"


def test_alter_column_set2() -> None:
    q = AlterTable("t").Alter.Column("c").SetNotNull.OnConflict.Fail
    assert q.get_query() == "ALTER TABLE t ALTER COLUMN c SET NOT NULL ON CONFLICT FAIL"


def test_alter_column_drop() -> None:
    q = AlterTable("t").Alter("c").DropNotNull
    assert q.get_query() == "ALTER TABLE t ALTER c DROP NOT NULL"
