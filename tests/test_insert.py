# SPEC: https://sqlite.org/lang_insert.html
#
# Full syntax from spec:
#   [WITH [RECURSIVE] common-table-expression [, ...]]
#   {INSERT | REPLACE | INSERT OR {ROLLBACK|ABORT|FAIL|IGNORE|REPLACE}}
#   INTO [schema-name.] table-name [AS alias]
#   [(column-name [, ...])]
#   {VALUES (expr [, ...]) [, ...] | select-stmt | DEFAULT VALUES}
#   [upsert-clause]
#   [RETURNING result-column [, ...]]
#
# =============================================================================
# NOT IMPLEMENTED:
# =============================================================================
# - ReturningClause._create_query is just `...`
# - OnConflictClause is abstract and raises NotImplementedError
# - SelectStatement placeholder needs real SELECT implementation
# - AliasedExpression placeholder for RETURNING clause


import sqlinpython.expression as expr
from sqlinpython import ColumnName
from sqlinpython.common_table_expression import (
    SelectStatement as CteSelectStatement,
)
from sqlinpython.common_table_expression import (
    TableName,
    With,
)
from sqlinpython.insert import (
    Insert_,
    Replace_,
    SelectStatement,
)
from sqlinpython.name import Name

# Entry point singletons (matching the pattern used elsewhere)
Insert = Insert_(None)
Replace = Replace_(None)


# =============================================================================
# Basic INSERT ... VALUES (simplest complete queries first)
# =============================================================================


def test_insert_values_simplest() -> None:
    # Most basic complete INSERT query
    assert (
        Insert.Into("t")("c").Values((expr.literal(1),)).get_query()
        == "INSERT INTO t (c) VALUES (1)"
    )


def test_insert_values_empty() -> None:
    # Edge case: empty VALUES tuple
    assert Insert.Into("t")("c").Values(()).get_query() == "INSERT INTO t (c) VALUES ()"


def test_insert_values_single_row() -> None:
    assert (
        Insert.Into("users")("id").Values((expr.literal(1),)).get_query()
        == "INSERT INTO users (id) VALUES (1)"
    )


def test_insert_values_multiple_columns() -> None:
    assert (
        Insert.Into("users")("id", "name")
        .Values((expr.literal(1), expr.literal("Alice")))
        .get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice")'
    )


def test_insert_values_multiple_rows() -> None:
    assert (
        Insert.Into("users")("id")
        .Values((expr.literal(1),), (expr.literal(2),), (expr.literal(3),))
        .get_query()
        == "INSERT INTO users (id) VALUES (1), (2), (3)"
    )


def test_insert_values_multiple_rows_multiple_columns() -> None:
    assert (
        Insert.Into("users")("id", "name")
        .Values(
            (expr.literal(1), expr.literal("Alice")),
            (expr.literal(2), expr.literal("Bob")),
        )
        .get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice"), (2, "Bob")'
    )


def test_insert_values_various_types() -> None:
    # VALUES with various expression types
    assert (
        Insert.Into("t")("a", "b", "c", "d")
        .Values(
            (
                expr.literal(1),
                expr.literal("text"),
                expr.literal(3.14),
                expr.literal(True),
            )
        )
        .get_query()
        == 'INSERT INTO t (a, b, c, d) VALUES (1, "text", 3.14, TRUE)'
    )


# =============================================================================
# INSERT ... DEFAULT VALUES
# =============================================================================


def test_insert_default_values_simple() -> None:
    assert (
        Insert.Into("users").DefaultValues.get_query()
        == "INSERT INTO users DEFAULT VALUES"
    )


def test_insert_default_values_with_columns() -> None:
    assert (
        Insert.Into("users")("id").DefaultValues.get_query()
        == "INSERT INTO users (id) DEFAULT VALUES"
    )


def test_insert_default_values_with_alias() -> None:
    assert (
        Insert.Into("users").As("u").DefaultValues.get_query()
        == "INSERT INTO users AS u DEFAULT VALUES"
    )


# =============================================================================
# INSERT ... SELECT (using placeholder)
# =============================================================================


def test_insert_select_simple() -> None:
    select_stmt = SelectStatement()
    assert (
        Insert.Into("users")(select_stmt).get_query()
        == "INSERT INTO users <select-stmt>"
    )


def test_insert_select_with_columns() -> None:
    select_stmt = SelectStatement()
    assert (
        Insert.Into("users")("id", "name")(select_stmt).get_query()
        == "INSERT INTO users (id, name) <select-stmt>"
    )


# =============================================================================
# Schema and alias variations (complete queries)
# =============================================================================


def test_insert_with_schema() -> None:
    assert (
        Insert.Into("main", "users")("id").Values((expr.literal(1),)).get_query()
        == "INSERT INTO main.users (id) VALUES (1)"
    )


def test_insert_with_alias() -> None:
    assert (
        Insert.Into("users").As("u")("id").Values((expr.literal(1),)).get_query()
        == "INSERT INTO users AS u (id) VALUES (1)"
    )


def test_insert_with_schema_and_alias() -> None:
    assert (
        Insert.Into("main", "users")
        .As("u")("id")
        .Values((expr.literal(1),))
        .get_query()
        == "INSERT INTO main.users AS u (id) VALUES (1)"
    )


def test_insert_quoted_names() -> None:
    # Names with special characters should be quoted
    assert (
        Insert.Into("my table")("user id").Values((expr.literal(1),)).get_query()
        == 'INSERT INTO "my table" ("user id") VALUES (1)'
    )


def test_insert_with_name_objects() -> None:
    assert (
        Insert.Into("users")(Name("id"), Name("name"))
        .Values((expr.literal(1), expr.literal("Alice")))
        .get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice")'
    )


# =============================================================================
# INSERT OR {ROLLBACK|ABORT|FAIL|IGNORE|REPLACE} (complete queries)
# =============================================================================


def test_insert_or_abort_values() -> None:
    assert (
        Insert.Or.Abort.Into("users")("id").Values((expr.literal(1),)).get_query()
        == "INSERT OR ABORT INTO users (id) VALUES (1)"
    )


def test_insert_or_fail_values() -> None:
    assert (
        Insert.Or.Fail.Into("users")("id").Values((expr.literal(1),)).get_query()
        == "INSERT OR FAIL INTO users (id) VALUES (1)"
    )


def test_insert_or_ignore_values() -> None:
    assert (
        Insert.Or.Ignore.Into("users")("id").Values((expr.literal(1),)).get_query()
        == "INSERT OR IGNORE INTO users (id) VALUES (1)"
    )


def test_insert_or_replace_values() -> None:
    assert (
        Insert.Or.Replace.Into("users")("id").Values((expr.literal(1),)).get_query()
        == "INSERT OR REPLACE INTO users (id) VALUES (1)"
    )


def test_insert_or_rollback_values() -> None:
    assert (
        Insert.Or.Rollback.Into("users")("id").Values((expr.literal(1),)).get_query()
        == "INSERT OR ROLLBACK INTO users (id) VALUES (1)"
    )


# =============================================================================
# REPLACE statement (complete queries)
# =============================================================================


def test_replace_values() -> None:
    assert (
        Replace.Into("users")("id").Values((expr.literal(1),)).get_query()
        == "REPLACE INTO users (id) VALUES (1)"
    )


def test_replace_default_values() -> None:
    assert (
        Replace.Into("users").DefaultValues.get_query()
        == "REPLACE INTO users DEFAULT VALUES"
    )


# =============================================================================
# WITH clause (complete queries)
# =============================================================================


def test_with_cte_insert_values() -> None:
    cte = TableName("temp").As(CteSelectStatement())
    assert (
        With(cte).Insert.Into("users")("id").Values((expr.literal(1),)).get_query()
        == "WITH temp AS (<select-stmt>) INSERT INTO users (id) VALUES (1)"
    )


def test_with_cte_insert_default_values() -> None:
    cte = TableName("temp").As(CteSelectStatement())
    assert (
        With(cte).Insert.Into("users").DefaultValues.get_query()
        == "WITH temp AS (<select-stmt>) INSERT INTO users DEFAULT VALUES"
    )


def test_with_cte_replace_values() -> None:
    cte = TableName("temp").As(CteSelectStatement())
    assert (
        With(cte).Replace.Into("users")("id").Values((expr.literal(1),)).get_query()
        == "WITH temp AS (<select-stmt>) REPLACE INTO users (id) VALUES (1)"
    )


def test_with_recursive_cte_insert() -> None:
    cte = TableName("recursive_t").As(CteSelectStatement())
    assert (
        With.Recursive(cte).Insert.Into("users").DefaultValues.get_query()
        == "WITH RECURSIVE recursive_t AS (<select-stmt>) INSERT INTO users DEFAULT VALUES"
    )


def test_with_multiple_ctes_insert() -> None:
    cte1 = TableName("t1").As(CteSelectStatement())
    cte2 = TableName("t2")("a", "b").As(CteSelectStatement())
    assert (
        With(cte1, cte2)
        .Insert.Into("target")("x")
        .Values((expr.literal(1),))
        .get_query()
        == "WITH t1 AS (<select-stmt>), t2(a, b) AS (<select-stmt>) INSERT INTO target (x) VALUES (1)"
    )


def test_with_cte_insert_select() -> None:
    cte = TableName("source").As(CteSelectStatement())
    select_stmt = SelectStatement()
    assert (
        With(cte).Insert.Into("target")(select_stmt).get_query()
        == "WITH source AS (<select-stmt>) INSERT INTO target <select-stmt>"
    )


# =============================================================================
# ON CONFLICT (upsert-clause)
# SPEC: https://sqlite.org/lang_upsert.html
#
# upsert-clause:
#   ON CONFLICT [conflict-target] DO NOTHING
#   ON CONFLICT [conflict-target] DO UPDATE SET ...
#
# conflict-target:
#   (indexed-column [, ...]) [WHERE expr]
# =============================================================================


def test_on_conflict_do_nothing_simple() -> None:
    # ON CONFLICT (col) DO NOTHING
    col = ColumnName("id")
    assert (
        Insert.Into("users")("id", "name")
        .Values((expr.literal(1), expr.literal("Alice")))
        .OnConflict(col)
        .Do.Nothing.get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice") ON CONFLICT(id) DO NOTHING'
    )


def test_on_conflict_do_nothing_multiple_columns() -> None:
    # ON CONFLICT (col1, col2) DO NOTHING
    col1 = ColumnName("id")
    col2 = ColumnName("email")
    assert (
        Insert.Into("users")("id", "email", "name")
        .Values((expr.literal(1), expr.literal("a@b.com"), expr.literal("Alice")))
        .OnConflict(col1, col2)
        .Do.Nothing.get_query()
        == 'INSERT INTO users (id, email, name) VALUES (1, "a@b.com", "Alice") ON CONFLICT(id, email) DO NOTHING'
    )


def test_on_conflict_with_where() -> None:
    # ON CONFLICT (col) WHERE expr DO NOTHING
    col = ColumnName("id")
    assert (
        Insert.Into("users")("id", "name")
        .Values((expr.literal(1), expr.literal("Alice")))
        .OnConflict(col)
        .Where(col > expr.literal(0))
        .Do.Nothing.get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice") ON CONFLICT(id) WHERE id > 0 DO NOTHING'
    )


def test_on_conflict_column_with_collate() -> None:
    # ON CONFLICT (col COLLATE NOCASE) DO NOTHING
    col = ColumnName("name").Collate("NOCASE")
    assert (
        Insert.Into("users")("id", "name")
        .Values((expr.literal(1), expr.literal("Alice")))
        .OnConflict(col)
        .Do.Nothing.get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice") ON CONFLICT(name COLLATE NOCASE) DO NOTHING'
    )


def test_on_conflict_column_with_asc() -> None:
    # ON CONFLICT (col ASC) DO NOTHING
    col = ColumnName("id").Asc
    assert (
        Insert.Into("users")("id", "name")
        .Values((expr.literal(1), expr.literal("Alice")))
        .OnConflict(col)
        .Do.Nothing.get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice") ON CONFLICT(id ASC) DO NOTHING'
    )


def test_on_conflict_column_with_desc() -> None:
    # ON CONFLICT (col DESC) DO NOTHING
    col = ColumnName("id").Desc
    assert (
        Insert.Into("users")("id", "name")
        .Values((expr.literal(1), expr.literal("Alice")))
        .OnConflict(col)
        .Do.Nothing.get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice") ON CONFLICT(id DESC) DO NOTHING'
    )


def test_on_conflict_column_with_collate_and_asc() -> None:
    # ON CONFLICT (col COLLATE NOCASE ASC) DO NOTHING
    col = ColumnName("name").Collate("NOCASE").Asc
    assert (
        Insert.Into("users")("id", "name")
        .Values((expr.literal(1), expr.literal("Alice")))
        .OnConflict(col)
        .Do.Nothing.get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice") ON CONFLICT(name COLLATE NOCASE ASC) DO NOTHING'
    )


def test_on_conflict_with_insert_select() -> None:
    # INSERT ... SELECT ... ON CONFLICT DO NOTHING
    col = ColumnName("id")
    select_stmt = SelectStatement()
    assert (
        Insert.Into("users")(select_stmt).OnConflict(col).Do.Nothing.get_query()
        == "INSERT INTO users <select-stmt> ON CONFLICT(id) DO NOTHING"
    )


# =============================================================================
# ON CONFLICT DO UPDATE SET
# SPEC: https://sqlite.org/lang_upsert.html
# =============================================================================


def test_on_conflict_do_update_set_single_column() -> None:
    # ON CONFLICT (col) DO UPDATE SET col = expr
    col = ColumnName("id")
    assert (
        Insert.Into("users")("id", "name")
        .Values((expr.literal(1), expr.literal("Alice")))
        .OnConflict(col)
        .Do.UpdateSet((ColumnName("name"), expr.literal("Updated")))
        .get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice") ON CONFLICT(id) DO UPDATE SET name = "Updated"'
    )


def test_on_conflict_do_update_set_string_column() -> None:
    # Using string for column name
    col = ColumnName("id")
    assert (
        Insert.Into("users")("id", "name")
        .Values((expr.literal(1), expr.literal("Alice")))
        .OnConflict(col)
        .Do.UpdateSet(("name", expr.literal("Updated")))
        .get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice") ON CONFLICT(id) DO UPDATE SET name = "Updated"'
    )


def test_on_conflict_do_update_set_multiple_assignments() -> None:
    # ON CONFLICT (col) DO UPDATE SET col1 = expr1, col2 = expr2
    col = ColumnName("id")
    assert (
        Insert.Into("users")("id", "name", "email")
        .Values((expr.literal(1), expr.literal("Alice"), expr.literal("a@b.com")))
        .OnConflict(col)
        .Do.UpdateSet(
            ("name", expr.literal("Updated")),
            ("email", expr.literal("new@email.com")),
        )
        .get_query()
        == 'INSERT INTO users (id, name, email) VALUES (1, "Alice", "a@b.com") ON CONFLICT(id) DO UPDATE SET name = "Updated", email = "new@email.com"'
    )


def test_on_conflict_do_update_set_column_list() -> None:
    # ON CONFLICT (col) DO UPDATE SET (col1, col2) = expr
    # This is used for row value assignments
    col = ColumnName("id")
    assert (
        Insert.Into("users")("id", "name", "email")
        .Values((expr.literal(1), expr.literal("Alice"), expr.literal("a@b.com")))
        .OnConflict(col)
        .Do.UpdateSet((("name", "email"), expr.literal("some_expr")))
        .get_query()
        == 'INSERT INTO users (id, name, email) VALUES (1, "Alice", "a@b.com") ON CONFLICT(id) DO UPDATE SET (name, email) = "some_expr"'
    )


def test_on_conflict_do_update_set_with_where() -> None:
    # ON CONFLICT (col) DO UPDATE SET col = expr WHERE condition
    col = ColumnName("id")
    name_col = ColumnName("name")
    assert (
        Insert.Into("users")("id", "name")
        .Values((expr.literal(1), expr.literal("Alice")))
        .OnConflict(col)
        .Do.UpdateSet(("name", expr.literal("Updated")))
        .Where(name_col.ne(expr.literal("Admin")))
        .get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice") ON CONFLICT(id) DO UPDATE SET name = "Updated" WHERE name != "Admin"'
    )


def test_on_conflict_do_update_set_with_conflict_where() -> None:
    # ON CONFLICT (col) WHERE expr DO UPDATE SET col = expr
    col = ColumnName("id")
    assert (
        Insert.Into("users")("id", "name")
        .Values((expr.literal(1), expr.literal("Alice")))
        .OnConflict(col)
        .Where(col > expr.literal(0))
        .Do.UpdateSet(("name", expr.literal("Updated")))
        .get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice") ON CONFLICT(id) WHERE id > 0 DO UPDATE SET name = "Updated"'
    )


# =============================================================================
# RETURNING clause
# SPEC: https://sqlite.org/lang_returning.html
# =============================================================================


def test_returning_star() -> None:
    # RETURNING *
    assert (
        Insert.Into("users")("id", "name")
        .Values((expr.literal(1), expr.literal("Alice")))
        .Returning("*")
        .get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice") RETURNING *'
    )


def test_returning_single_column() -> None:
    # RETURNING expr
    col = ColumnName("id")
    assert (
        Insert.Into("users")("id", "name")
        .Values((expr.literal(1), expr.literal("Alice")))
        .Returning(col)
        .get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice") RETURNING id'
    )


def test_returning_expression() -> None:
    # RETURNING with an expression
    col = ColumnName("id")
    assert (
        Insert.Into("users")("id", "name")
        .Values((expr.literal(1), expr.literal("Alice")))
        .Returning(col + expr.literal(1))
        .get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice") RETURNING id + 1'
    )


def test_returning_with_alias() -> None:
    # RETURNING expr AS alias
    col = ColumnName("id")
    assert (
        Insert.Into("users")("id", "name")
        .Values((expr.literal(1), expr.literal("Alice")))
        .Returning(col.As("user_id"))
        .get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice") RETURNING id AS user_id'
    )


def test_returning_multiple_columns() -> None:
    # RETURNING col1, col2
    id_col = ColumnName("id")
    name_col = ColumnName("name")
    assert (
        Insert.Into("users")("id", "name")
        .Values((expr.literal(1), expr.literal("Alice")))
        .Returning(id_col, name_col)
        .get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice") RETURNING id, name'
    )


def test_returning_multiple_with_aliases() -> None:
    # RETURNING col1 AS alias1, col2 AS alias2
    id_col = ColumnName("id")
    name_col = ColumnName("name")
    assert (
        Insert.Into("users")("id", "name")
        .Values((expr.literal(1), expr.literal("Alice")))
        .Returning(id_col.As("user_id"), name_col.As("user_name"))
        .get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice") RETURNING id AS user_id, name AS user_name'
    )


def test_returning_with_default_values() -> None:
    # INSERT ... DEFAULT VALUES RETURNING *
    assert (
        Insert.Into("users").DefaultValues.Returning("*").get_query()
        == "INSERT INTO users DEFAULT VALUES RETURNING *"
    )


def test_returning_with_on_conflict() -> None:
    # INSERT ... ON CONFLICT DO NOTHING RETURNING *
    col = ColumnName("id")
    assert (
        Insert.Into("users")("id", "name")
        .Values((expr.literal(1), expr.literal("Alice")))
        .OnConflict(col)
        .Do.Nothing.Returning("*")
        .get_query()
        == 'INSERT INTO users (id, name) VALUES (1, "Alice") ON CONFLICT(id) DO NOTHING RETURNING *'
    )


def test_replace_returning() -> None:
    # REPLACE ... RETURNING *
    assert (
        Replace.Into("users")("id").Values((expr.literal(1),)).Returning("*").get_query()
        == "REPLACE INTO users (id) VALUES (1) RETURNING *"
    )
