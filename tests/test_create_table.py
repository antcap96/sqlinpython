from sqlinpython import (
    Check,
    ColumnName,
    Constraint,
    Create,
    CurrentDate,
    ForeignKey,
    PrimaryKey,
    Select,
    TypeName,
    Unique,
    literal,
)

a = ColumnName("a")
b = ColumnName("b")
select_stmt = Select(literal(1))


# ---------------------------------------------------------------------------
# CREATE TABLE
# ---------------------------------------------------------------------------


def test_create_table_as_select() -> None:
    q = Create.Table("table_name").As(select_stmt)
    assert q.get_query() == "CREATE TABLE table_name AS SELECT 1"


def test_create_temp_table_schema_qualified() -> None:
    q = Create.Temp.Table("schema_name", "table_name").As(select_stmt)
    assert q.get_query() == "CREATE TEMP TABLE schema_name.table_name AS SELECT 1"


def test_create_temporary_table_schema_qualified() -> None:
    q = Create.Temporary.Table("schema_name", "table_name").As(select_stmt)
    assert q.get_query() == "CREATE TEMPORARY TABLE schema_name.table_name AS SELECT 1"


def test_create_table_if_not_exists() -> None:
    q = Create.Table.IfNotExists("table_name").As(select_stmt)
    assert q.get_query() == "CREATE TABLE IF NOT EXISTS table_name AS SELECT 1"


def test_create_table_schema_qualified() -> None:
    q = Create.Table("schema_name", "table_name").As(select_stmt)
    assert q.get_query() == "CREATE TABLE schema_name.table_name AS SELECT 1"


def test_create_table_single_column() -> None:
    q = Create.Table("table_name")(a)
    assert q.get_query() == "CREATE TABLE table_name (a)"


def test_create_table_two_columns() -> None:
    q = Create.Table("table_name")(a, b)
    assert q.get_query() == "CREATE TABLE table_name (a, b)"


def test_create_table_strict() -> None:
    q = Create.Table("table_name")(a).Strict
    assert q.get_query() == "CREATE TABLE table_name (a) STRICT"


def test_create_table_without_rowid() -> None:
    q = Create.Table("table_name")(a).WithoutRowId
    assert q.get_query() == "CREATE TABLE table_name (a) WITHOUT ROWID"


def test_create_table_strict_without_rowid() -> None:
    q = Create.Table("table_name")(a).Strict.WithoutRowId
    assert q.get_query() == "CREATE TABLE table_name (a) STRICT, WITHOUT ROWID"


def test_create_table_without_rowid_strict() -> None:
    q = Create.Table("table_name")(a).WithoutRowId.Strict
    assert q.get_query() == "CREATE TABLE table_name (a) WITHOUT ROWID, STRICT"


# ---------------------------------------------------------------------------
# Column definitions
# ---------------------------------------------------------------------------


def test_column_definition_bare() -> None:
    q = Create.Table("table_name")(a)
    assert q.get_query() == "CREATE TABLE table_name (a)"


def test_column_definition_constraint_primary_key() -> None:
    q = Create.Table("table_name")(a.Constraint("b").PrimaryKey)
    assert q.get_query() == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY)"


def test_column_definition_constraint_primary_key_asc() -> None:
    q = Create.Table("table_name")(a.Constraint("b").PrimaryKey.Asc)
    assert q.get_query() == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY ASC)"


def test_column_definition_constraint_primary_key_desc() -> None:
    q = Create.Table("table_name")(a.Constraint("b").PrimaryKey.Desc)
    assert q.get_query() == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY DESC)"


def test_column_definition_constraint_primary_key_autoincrement() -> None:
    q = Create.Table("table_name")(a.Constraint("b").PrimaryKey.AutoIncrement)
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY AUTOINCREMENT)"
    )


def test_column_definition_constraint_primary_key_on_conflict_rollback() -> None:
    q = Create.Table("table_name")(a.Constraint("b").PrimaryKey.OnConflict.Rollback)
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY ON CONFLICT ROLLBACK)"
    )


def test_column_definition_constraint_primary_key_on_conflict_abort() -> None:
    q = Create.Table("table_name")(a.Constraint("b").PrimaryKey.OnConflict.Abort)
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY ON CONFLICT ABORT)"
    )


def test_column_definition_constraint_primary_key_on_conflict_fail() -> None:
    q = Create.Table("table_name")(a.Constraint("b").PrimaryKey.OnConflict.Fail)
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY ON CONFLICT FAIL)"
    )


def test_column_definition_constraint_primary_key_on_conflict_ignore() -> None:
    q = Create.Table("table_name")(a.Constraint("b").PrimaryKey.OnConflict.Ignore)
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY ON CONFLICT IGNORE)"
    )


def test_column_definition_constraint_primary_key_on_conflict_replace() -> None:
    q = Create.Table("table_name")(a.Constraint("b").PrimaryKey.OnConflict.Replace)
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY ON CONFLICT REPLACE)"
    )


def test_column_definition_constraint_primary_key_on_conflict_replace_autoincrement() -> (
    None
):
    q = Create.Table("table_name")(
        a.Constraint("b").PrimaryKey.OnConflict.Replace.AutoIncrement
    )
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a CONSTRAINT b PRIMARY KEY ON CONFLICT REPLACE AUTOINCREMENT)"
    )


def test_column_definition_not_null() -> None:
    q = Create.Table("table_name")(a.NotNull)
    assert q.get_query() == "CREATE TABLE table_name (a NOT NULL)"


def test_column_definition_not_null_on_conflict_rollback() -> None:
    q = Create.Table("table_name")(a.NotNull.OnConflict.Rollback)
    assert q.get_query() == "CREATE TABLE table_name (a NOT NULL ON CONFLICT ROLLBACK)"


def test_column_definition_not_null_on_conflict_abort() -> None:
    q = Create.Table("table_name")(a.NotNull.OnConflict.Abort)
    assert q.get_query() == "CREATE TABLE table_name (a NOT NULL ON CONFLICT ABORT)"


def test_column_definition_not_null_on_conflict_fail() -> None:
    q = Create.Table("table_name")(a.NotNull.OnConflict.Fail)
    assert q.get_query() == "CREATE TABLE table_name (a NOT NULL ON CONFLICT FAIL)"


def test_column_definition_not_null_on_conflict_ignore() -> None:
    q = Create.Table("table_name")(a.NotNull.OnConflict.Ignore)
    assert q.get_query() == "CREATE TABLE table_name (a NOT NULL ON CONFLICT IGNORE)"


def test_column_definition_not_null_on_conflict_replace() -> None:
    q = Create.Table("table_name")(a.NotNull.OnConflict.Replace)
    assert q.get_query() == "CREATE TABLE table_name (a NOT NULL ON CONFLICT REPLACE)"


def test_column_definition_unique() -> None:
    q = Create.Table("table_name")(a.Unique)
    assert q.get_query() == "CREATE TABLE table_name (a UNIQUE)"


def test_column_definition_unique_on_conflict_rollback() -> None:
    q = Create.Table("table_name")(a.Unique.OnConflict.Rollback)
    assert q.get_query() == "CREATE TABLE table_name (a UNIQUE ON CONFLICT ROLLBACK)"


def test_column_definition_default_int() -> None:
    q = Create.Table("table_name")(a.Default(1))
    assert q.get_query() == "CREATE TABLE table_name (a DEFAULT 1)"


def test_column_definition_default_not_null() -> None:
    q = Create.Table("table_name")(a.Default(1).NotNull)
    assert q.get_query() == "CREATE TABLE table_name (a DEFAULT 1 NOT NULL)"


def test_column_definition_default_literal_unique() -> None:
    q = Create.Table("table_name")(a.Default(literal(1)).Unique)
    assert q.get_query() == "CREATE TABLE table_name (a DEFAULT 1 UNIQUE)"


def test_column_definition_default_string_unique() -> None:
    q = Create.Table("table_name")(a.Default(literal("a")).Unique)
    assert q.get_query() == 'CREATE TABLE table_name (a DEFAULT "a" UNIQUE)'


def test_column_definition_default_current_date_not_null_unique() -> None:
    q = Create.Table("table_name")(a.Default(CurrentDate).NotNull.Unique)
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a DEFAULT CURRENT_DATE NOT NULL UNIQUE)"
    )


def test_column_definition_default_force_parenthesis_int() -> None:
    q = Create.Table("table_name")(a.Default(1, force_parenthesis=True))
    assert q.get_query() == "CREATE TABLE table_name (a DEFAULT (1))"


def test_column_definition_default_force_parenthesis_literal() -> None:
    q = Create.Table("table_name")(a.Default(literal("a"), force_parenthesis=True))
    assert q.get_query() == 'CREATE TABLE table_name (a DEFAULT ("a"))'


def test_column_definition_default_expression() -> None:
    q = Create.Table("table_name")(a.Default(b + literal(1)))
    assert q.get_query() == "CREATE TABLE table_name (a DEFAULT (b + 1))"


def test_column_definition_check() -> None:
    q = Create.Table("table_name")(a.Check(b > literal(0)))
    assert q.get_query() == "CREATE TABLE table_name (a CHECK (b > 0))"


def test_column_definition_check_not_null() -> None:
    q = Create.Table("table_name")(a.Check(b > literal(0)).NotNull)
    assert q.get_query() == "CREATE TABLE table_name (a CHECK (b > 0) NOT NULL)"


def test_column_definition_named_check() -> None:
    q = Create.Table("table_name")(a.Constraint("c").Check(b > literal(0)))
    assert q.get_query() == "CREATE TABLE table_name (a CONSTRAINT c CHECK (b > 0))"


def test_column_definition_collate() -> None:
    q = Create.Table("table_name")(a.Collate("utf8"))
    assert q.get_query() == "CREATE TABLE table_name (a COLLATE utf8)"


def test_column_definition_as_generated() -> None:
    q = Create.Table("table_name")(a.As(literal("a")))
    assert q.get_query() == 'CREATE TABLE table_name (a AS ("a"))'


def test_column_definition_collate_as_generated() -> None:
    q = Create.Table("table_name")(a.Collate("utf8").As(literal("a")))
    assert q.get_query() == 'CREATE TABLE table_name (a COLLATE utf8 AS ("a"))'


def test_column_definition_collate_collate_as_generated() -> None:
    q = Create.Table("table_name")(a.Collate("utf8").Collate("utf16").As(literal("a")))
    assert (
        q.get_query()
        == 'CREATE TABLE table_name (a COLLATE utf8 COLLATE utf16 AS ("a"))'
    )


def test_column_definition_generated_always_as() -> None:
    q = Create.Table("table_name")(a.GeneratedAlways.As(literal("a")))
    assert q.get_query() == 'CREATE TABLE table_name (a GENERATED ALWAYS AS ("a"))'


def test_column_definition_generated_always_as_stored() -> None:
    q = Create.Table("table_name")(a.GeneratedAlways.As(literal("a")).Stored)
    assert (
        q.get_query() == 'CREATE TABLE table_name (a GENERATED ALWAYS AS ("a") STORED)'
    )


def test_column_definition_generated_always_as_virtual() -> None:
    q = Create.Table("table_name")(a.GeneratedAlways.As(literal("a")).Virtual)
    assert (
        q.get_query() == 'CREATE TABLE table_name (a GENERATED ALWAYS AS ("a") VIRTUAL)'
    )


# ---------------------------------------------------------------------------
# Type names
# ---------------------------------------------------------------------------


def test_type_name_integer() -> None:
    q = Create.Table("table_name")(a(TypeName("INTEGER")))
    assert q.get_query() == "CREATE TABLE table_name (a INTEGER)"


def test_type_name_decimal_one_arg() -> None:
    q = Create.Table("table_name")(a(TypeName("DECIMAL")(1)))
    assert q.get_query() == "CREATE TABLE table_name (a DECIMAL(1))"


def test_type_name_decimal_two_args() -> None:
    q = Create.Table("table_name")(a(TypeName("DECIMAL")(1, 2)))
    assert q.get_query() == "CREATE TABLE table_name (a DECIMAL(1, 2))"


def test_type_name_with_constraint() -> None:
    q = Create.Table("table_name")(a(TypeName("INTEGER")).NotNull)
    assert q.get_query() == "CREATE TABLE table_name (a INTEGER NOT NULL)"


# ---------------------------------------------------------------------------
# Table constraints
# ---------------------------------------------------------------------------


def test_table_constraint_named_primary_key() -> None:
    q = Create.Table("table_name")(a, Constraint("pk").PrimaryKey(a))
    assert q.get_query() == "CREATE TABLE table_name (a, CONSTRAINT pk PRIMARY KEY (a))"


def test_table_constraint_primary_key_single() -> None:
    q = Create.Table("table_name")(a, PrimaryKey(a))
    assert q.get_query() == "CREATE TABLE table_name (a, PRIMARY KEY (a))"


def test_table_constraint_primary_key_multiple() -> None:
    q = Create.Table("table_name")(a, PrimaryKey(a, b))
    assert q.get_query() == "CREATE TABLE table_name (a, PRIMARY KEY (a, b))"


def test_table_constraint_primary_key_autoincrement() -> None:
    q = Create.Table("table_name")(a, PrimaryKey(a, autoincrement=True))
    assert q.get_query() == "CREATE TABLE table_name (a, PRIMARY KEY (a AUTOINCREMENT))"


def test_table_constraint_primary_key_on_conflict_fail() -> None:
    q = Create.Table("table_name")(a, PrimaryKey(a).OnConflict().Fail)
    assert (
        q.get_query() == "CREATE TABLE table_name (a, PRIMARY KEY (a) ON CONFLICT FAIL)"
    )


def test_table_constraint_named_unique() -> None:
    q = Create.Table("table_name")(a, Constraint("uq").Unique(a))
    assert q.get_query() == "CREATE TABLE table_name (a, CONSTRAINT uq UNIQUE (a))"


def test_table_constraint_unique_single() -> None:
    q = Create.Table("table_name")(a, Unique(a))
    assert q.get_query() == "CREATE TABLE table_name (a, UNIQUE (a))"


def test_table_constraint_unique_multiple() -> None:
    q = Create.Table("table_name")(a, Unique(a, b))
    assert q.get_query() == "CREATE TABLE table_name (a, UNIQUE (a, b))"


def test_table_constraint_unique_asc_desc() -> None:
    q = Create.Table("table_name")(a, Unique(a.Asc, b.Desc))
    assert q.get_query() == "CREATE TABLE table_name (a, UNIQUE (a ASC, b DESC))"


def test_table_constraint_unique_on_conflict_rollback() -> None:
    q = Create.Table("table_name")(a, Unique(a).OnConflict().Rollback)
    assert (
        q.get_query() == "CREATE TABLE table_name (a, UNIQUE (a) ON CONFLICT ROLLBACK)"
    )


def test_table_constraint_named_check() -> None:
    q = Create.Table("table_name")(
        a, Constraint("check").Check(literal(1) > literal(0))
    )
    assert (
        q.get_query() == "CREATE TABLE table_name (a, CONSTRAINT check CHECK (1 > 0))"
    )


def test_table_constraint_check() -> None:
    q = Create.Table("table_name")(a, Check(literal(1) > literal(0)))
    assert q.get_query() == "CREATE TABLE table_name (a, CHECK (1 > 0))"


def test_table_constraint_named_foreign_key() -> None:
    q = Create.Table("table_name")(a, Constraint("fk").ForeignKey("b").References("c"))
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a, CONSTRAINT fk FOREIGN KEY(b) REFERENCES c)"
    )


def test_table_constraint_foreign_key() -> None:
    q = Create.Table("table_name")(a, ForeignKey("b").References("c"))
    assert q.get_query() == "CREATE TABLE table_name (a, FOREIGN KEY(b) REFERENCES c)"


def test_table_constraint_foreign_key_not_deferrable() -> None:
    q = Create.Table("table_name")(a, ForeignKey("b").References("c").Not.Deferrable)
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a, FOREIGN KEY(b) REFERENCES c NOT DEFERRABLE)"
    )


# ---------------------------------------------------------------------------
# Foreign key clause
# ---------------------------------------------------------------------------


def test_foreign_key_clause_named_references() -> None:
    q = Create.Table("table_name")(a.Constraint("c").References("d"))
    assert q.get_query() == "CREATE TABLE table_name (a CONSTRAINT c REFERENCES d)"


def test_foreign_key_clause_references_basic() -> None:
    q = Create.Table("table_name")(a.References("d"))
    assert q.get_query() == "CREATE TABLE table_name (a REFERENCES d)"


def test_foreign_key_clause_references_columns() -> None:
    q = Create.Table("table_name")(a.References("d")("x", "y"))
    assert q.get_query() == "CREATE TABLE table_name (a REFERENCES d (x, y))"


def test_foreign_key_clause_on_update_set_null() -> None:
    q = Create.Table("table_name")(a.References("d")("x").On.Update.SetNull)
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a REFERENCES d (x) ON UPDATE SET NULL)"
    )


def test_foreign_key_clause_on_update_set_default() -> None:
    q = Create.Table("table_name")(a.References("d")("x").On.Update.SetDefault)
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a REFERENCES d (x) ON UPDATE SET DEFAULT)"
    )


def test_foreign_key_clause_on_update_cascade() -> None:
    q = Create.Table("table_name")(a.References("d")("x").On.Update.Cascade)
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a REFERENCES d (x) ON UPDATE CASCADE)"
    )


def test_foreign_key_clause_on_update_restrict() -> None:
    q = Create.Table("table_name")(a.References("d")("x").On.Update.Restrict)
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a REFERENCES d (x) ON UPDATE RESTRICT)"
    )


def test_foreign_key_clause_on_update_no_action() -> None:
    q = Create.Table("table_name")(a.References("d")("x").On.Update.NoAction)
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a REFERENCES d (x) ON UPDATE NO ACTION)"
    )


def test_foreign_key_clause_match() -> None:
    q = Create.Table("table_name")(a.References("d")("x").Match("d"))
    assert q.get_query() == "CREATE TABLE table_name (a REFERENCES d (x) MATCH d)"


def test_foreign_key_clause_match_on_delete_cascade() -> None:
    q = Create.Table("table_name")(a.References("d")("x").Match("d").On.Delete.Cascade)
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a REFERENCES d (x) MATCH d ON DELETE CASCADE)"
    )


def test_foreign_key_clause_on_delete_cascade_match() -> None:
    q = Create.Table("table_name")(a.References("d")("x").On.Delete.Cascade.Match("d"))
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a REFERENCES d (x) ON DELETE CASCADE MATCH d)"
    )


def test_foreign_key_clause_on_delete_cascade_match_deferrable() -> None:
    q = Create.Table("table_name")(
        a.References("d")("x").On.Delete.Cascade.Match("d").Deferrable
    )
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a REFERENCES d (x) ON DELETE CASCADE MATCH d DEFERRABLE)"
    )


def test_foreign_key_clause_not_deferrable() -> None:
    q = Create.Table("table_name")(a.References("d").Not.Deferrable)
    assert q.get_query() == "CREATE TABLE table_name (a REFERENCES d NOT DEFERRABLE)"


def test_foreign_key_clause_not_deferrable_initially_deferred() -> None:
    q = Create.Table("table_name")(a.References("d").Not.Deferrable.Initially.Deferred)
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a REFERENCES d NOT DEFERRABLE INITIALLY DEFERRED)"
    )


def test_foreign_key_clause_deferrable_initially_immediate() -> None:
    q = Create.Table("table_name")(a.References("d").Deferrable.Initially.Immediate)
    assert (
        q.get_query()
        == "CREATE TABLE table_name (a REFERENCES d DEFERRABLE INITIALLY IMMEDIATE)"
    )


def test_create_table_doesnt_accept_table_constraint() -> None:
    Create.Table("table_name")(
        Constraint("a").ForeignKey("b").References("t")  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
        # ty doesn't currently identify this error -ty: ignore[invalid-argument]
    ).WithoutRowId.Strict
