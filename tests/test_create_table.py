import sqlinpython.expression as expr
from sqlinpython import (
    Check,
    ColumnName,
    Constraint,
    Create,
    PrimaryKey,
    TypeName,
    Unique,
)
from sqlinpython.create_table import SelectStatement
from sqlinpython.table_constraint import ForeignKey


def test_create_table() -> None:
    a = ColumnName("a")
    b = ColumnName("b")
    assert (
        Create.Table("table_name").As(SelectStatement("TODO")).get_query()
        == "CREATE TABLE table_name AS TODO"
    )
    assert (
        Create.Temp.Table("schema_name", "table_name")
        .As(SelectStatement("TODO"))
        .get_query()
        == "CREATE TEMP TABLE schema_name.table_name AS TODO"
    )
    assert (
        Create.Temporary.Table("schema_name", "table_name")
        .As(SelectStatement("TODO"))
        .get_query()
        == "CREATE TEMPORARY TABLE schema_name.table_name AS TODO"
    )
    assert (
        Create.Table.IfNotExists("table_name").As(SelectStatement("TODO")).get_query()
        == "CREATE TABLE IF NOT EXISTS table_name AS TODO"
    )
    assert (
        Create.Table("schema_name", "table_name")
        .As(SelectStatement("TODO"))
        .get_query()
        == "CREATE TABLE schema_name.table_name AS TODO"
    )
    assert Create.Table("table_name")(a).get_query() == "CREATE TABLE table_name (a)"
    assert (
        Create.Table("table_name")(a, b).get_query() == "CREATE TABLE table_name (a, b)"
    )
    assert (
        Create.Table("table_name")(a).Strict.get_query()
        == "CREATE TABLE table_name (a) STRICT"
    )
    assert (
        Create.Table("table_name")(a).WithoutRowId.get_query()
        == "CREATE TABLE table_name (a) WITHOUT ROWID"
    )
    assert (
        Create.Table("table_name")(a).Strict.WithoutRowId.get_query()
        == "CREATE TABLE table_name (a) STRICT, WITHOUT ROWID"
    )
    assert (
        Create.Table("table_name")(a).WithoutRowId.Strict.get_query()
        == "CREATE TABLE table_name (a) WITHOUT ROWID, STRICT"
    )


def test_column_definition() -> None:
    start = Create.Table("table_name")
    a = ColumnName("a")
    assert start(a).get_query() == "CREATE TABLE table_name (a)"
    assert (
        start(a.Constraint("b").PrimaryKey).get_query()
        == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY)"
    )
    assert (
        start(a.Constraint("b").PrimaryKey.Asc).get_query()
        == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY ASC)"
    )
    assert (
        start(a.Constraint("b").PrimaryKey.Desc).get_query()
        == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY DESC)"
    )
    assert (
        start(a.Constraint("b").PrimaryKey.AutoIncrement).get_query()
        == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY AUTOINCREMENT)"
    )
    assert (
        start(a.Constraint("b").PrimaryKey.OnConflict.Rollback).get_query()
        == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY ON CONFLICT ROLLBACK)"
    )
    assert (
        start(a.Constraint("b").PrimaryKey.OnConflict.Abort).get_query()
        == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY ON CONFLICT ABORT)"
    )
    assert (
        start(a.Constraint("b").PrimaryKey.OnConflict.Fail).get_query()
        == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY ON CONFLICT FAIL)"
    )
    assert (
        start(a.Constraint("b").PrimaryKey.OnConflict.Ignore).get_query()
        == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY ON CONFLICT IGNORE)"
    )
    assert (
        start(a.Constraint("b").PrimaryKey.OnConflict.Replace).get_query()
        == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY ON CONFLICT REPLACE)"
    )
    assert (
        start(a.Constraint("b").PrimaryKey.OnConflict.Replace.AutoIncrement).get_query()
        == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY ON CONFLICT REPLACE AUTOINCREMENT)"
    )
    assert start(a.NotNull).get_query() == "CREATE TABLE table_name (a NOT NULL)"
    assert (
        start(a.NotNull.OnConflict.Rollback).get_query()
        == "CREATE TABLE table_name (a NOT NULL ON CONFLICT ROLLBACK)"
    )
    assert (
        start(a.NotNull.OnConflict.Abort).get_query()
        == "CREATE TABLE table_name (a NOT NULL ON CONFLICT ABORT)"
    )
    assert (
        start(a.NotNull.OnConflict.Fail).get_query()
        == "CREATE TABLE table_name (a NOT NULL ON CONFLICT FAIL)"
    )
    assert (
        start(a.NotNull.OnConflict.Ignore).get_query()
        == "CREATE TABLE table_name (a NOT NULL ON CONFLICT IGNORE)"
    )
    assert (
        start(a.NotNull.OnConflict.Replace).get_query()
        == "CREATE TABLE table_name (a NOT NULL ON CONFLICT REPLACE)"
    )
    assert start(a.Unique).get_query() == "CREATE TABLE table_name (a UNIQUE)"
    assert (
        start(a.Unique.OnConflict.Rollback).get_query()
        == "CREATE TABLE table_name (a UNIQUE ON CONFLICT ROLLBACK)"
    )
    assert start(a.Default(1)).get_query() == "CREATE TABLE table_name (a DEFAULT 1)"
    assert (
        start(a.Default(1).NotNull).get_query()
        == "CREATE TABLE table_name (a DEFAULT 1 NOT NULL)"
    )
    assert (
        start(a.Default(expr.literal(1)).Unique).get_query()
        == "CREATE TABLE table_name (a DEFAULT 1 UNIQUE)"
    )
    assert (
        start(a.Default(expr.literal("a")).Unique).get_query()
        == 'CREATE TABLE table_name (a DEFAULT "a" UNIQUE)'
    )
    assert (
        start(a.Default(expr.CurrentDate).NotNull.Unique).get_query()
        == "CREATE TABLE table_name (a DEFAULT CURRENT_DATE NOT NULL UNIQUE)"
    )
    assert (
        start(a.Collate("utf8")).get_query()
        == "CREATE TABLE table_name (a COLLATE utf8)"
    )
    assert (
        start(a.As(expr.literal("a"))).get_query()
        == 'CREATE TABLE table_name (a AS ("a"))'
    )
    assert (
        start(a.GeneratedAlways.As(expr.literal("a"))).get_query()
        == 'CREATE TABLE table_name (a GENERATED ALWAYS AS ("a"))'
    )
    assert (
        start(a.GeneratedAlways.As(expr.literal("a")).Stored).get_query()
        == 'CREATE TABLE table_name (a GENERATED ALWAYS AS ("a") STORED)'
    )
    assert (
        start(a.GeneratedAlways.As(expr.literal("a")).Virtual).get_query()
        == 'CREATE TABLE table_name (a GENERATED ALWAYS AS ("a") VIRTUAL)'
    )


def test_type_name() -> None:
    start = Create.Table("table_name")
    a = ColumnName("a")
    assert (
        start(a(TypeName("INTEGER"))).get_query()
        == "CREATE TABLE table_name (a INTEGER)"
    )
    assert (
        start(a(TypeName("DECIMAL")(1))).get_query()
        == "CREATE TABLE table_name (a DECIMAL(1))"
    )
    assert (
        start(a(TypeName("DECIMAL")(1, 2))).get_query()
        == "CREATE TABLE table_name (a DECIMAL(1, 2))"
    )
    assert (
        start(a(TypeName("INTEGER")).NotNull).get_query()
        == "CREATE TABLE table_name (a INTEGER NOT NULL)"
    )


def test_table_constraint() -> None:
    start = Create.Table("table_name")
    a = ColumnName("a")
    b = ColumnName("b")
    assert (
        start(a, Constraint("pk").PrimaryKey(a)).get_query()
        == "CREATE TABLE table_name (a, CONSTRAINT pk PRIMARY KEY (a))"
    )
    assert (
        start(a, PrimaryKey(a)).get_query()
        == "CREATE TABLE table_name (a, PRIMARY KEY (a))"
    )
    assert (
        start(a, PrimaryKey(a, b)).get_query()
        == "CREATE TABLE table_name (a, PRIMARY KEY (a, b))"
    )
    assert (
        start(a, PrimaryKey(a, autoincrement=True)).get_query()
        == "CREATE TABLE table_name (a, PRIMARY KEY (a AUTOINCREMENT))"
    )
    assert (
        start(a, PrimaryKey(a).OnConflict().Fail).get_query()
        == "CREATE TABLE table_name (a, PRIMARY KEY (a) ON CONFLICT FAIL)"
    )
    assert (
        start(a, Constraint("uq").Unique(a)).get_query()
        == "CREATE TABLE table_name (a, CONSTRAINT uq UNIQUE (a))"
    )
    assert start(a, Unique(a)).get_query() == "CREATE TABLE table_name (a, UNIQUE (a))"
    assert (
        start(a, Unique(a, b)).get_query()
        == "CREATE TABLE table_name (a, UNIQUE (a, b))"
    )
    assert (
        start(a, Unique(a.Asc, b.Desc)).get_query()
        == "CREATE TABLE table_name (a, UNIQUE (a ASC, b DESC))"
    )
    assert (
        start(a, Unique(a).OnConflict().Rollback).get_query()
        == "CREATE TABLE table_name (a, UNIQUE (a) ON CONFLICT ROLLBACK)"
    )
    assert (
        start(
            a, Constraint("check").Check(expr.literal(1) > expr.literal(0))
        ).get_query()
        == "CREATE TABLE table_name (a, CONSTRAINT check CHECK (1 > 0))"
    )
    assert (
        start(a, Check(expr.literal(1) > expr.literal(0))).get_query()
        == "CREATE TABLE table_name (a, CHECK (1 > 0))"
    )
    assert (
        start(a, Constraint("fk").ForeignKey("b").References("c")).get_query()
        == "CREATE TABLE table_name (a, CONSTRAINT fk FOREIGN KEY(b) REFERENCES c)"
    )
    assert (
        start(a, ForeignKey("b").References("c")).get_query()
        == "CREATE TABLE table_name (a, FOREIGN KEY(b) REFERENCES c)"
    )
    assert (
        start(a, ForeignKey("b").References("c").Not.Deferrable).get_query()
        == "CREATE TABLE table_name (a, FOREIGN KEY(b) REFERENCES c NOT DEFERRABLE)"
    )


def test_foreign_key_clause() -> None:
    start = Create.Table("table_name")
    a = ColumnName("a")
    assert (
        start(a.Constraint("c").References("d")).get_query()
        == "CREATE TABLE table_name (a CONSTRAINT c REFERENCES d)"
    )
    assert (
        start(a.References("d")).get_query()
        == "CREATE TABLE table_name (a REFERENCES d)"
    )
    assert (
        start(a.References("d")("x", "y")).get_query()
        == "CREATE TABLE table_name (a REFERENCES d (x, y))"
    )
    assert (
        start(a.References("d")("x").On.Update.SetNull).get_query()
        == "CREATE TABLE table_name (a REFERENCES d (x) ON UPDATE SET NULL)"
    )
    assert (
        start(a.References("d")("x").On.Update.SetDefault).get_query()
        == "CREATE TABLE table_name (a REFERENCES d (x) ON UPDATE SET DEFAULT)"
    )
    assert (
        start(a.References("d")("x").On.Update.Cascade).get_query()
        == "CREATE TABLE table_name (a REFERENCES d (x) ON UPDATE CASCADE)"
    )
    assert (
        start(a.References("d")("x").On.Update.Restrict).get_query()
        == "CREATE TABLE table_name (a REFERENCES d (x) ON UPDATE RESTRICT)"
    )
    assert (
        start(a.References("d")("x").On.Update.NoAction).get_query()
        == "CREATE TABLE table_name (a REFERENCES d (x) ON UPDATE NO ACTION)"
    )
    assert (
        start(a.References("d")("x").Match("d")).get_query()
        == "CREATE TABLE table_name (a REFERENCES d (x) MATCH d)"
    )
    assert (
        start(a.References("d")("x").Match("d").On.Delete.Cascade).get_query()
        == "CREATE TABLE table_name (a REFERENCES d (x) MATCH d ON DELETE CASCADE)"
    )
    assert (
        start(a.References("d")("x").On.Delete.Cascade.Match("d")).get_query()
        == "CREATE TABLE table_name (a REFERENCES d (x) ON DELETE CASCADE MATCH d)"
    )
    assert (
        start(
            a.References("d")("x").On.Delete.Cascade.Match("d").Deferrable
        ).get_query()
        == "CREATE TABLE table_name (a REFERENCES d (x) ON DELETE CASCADE MATCH d DEFERRABLE)"
    )
    assert (
        start(a.References("d").Not.Deferrable).get_query()
        == "CREATE TABLE table_name (a REFERENCES d NOT DEFERRABLE)"
    )
    assert (
        start(a.References("d").Not.Deferrable.Initially.Deferred).get_query()
        == "CREATE TABLE table_name (a REFERENCES d NOT DEFERRABLE INITIALLY DEFERRED)"
    )
    assert (
        start(a.References("d").Deferrable.Initially.Immediate).get_query()
        == "CREATE TABLE table_name (a REFERENCES d DEFERRABLE INITIALLY IMMEDIATE)"
    )
