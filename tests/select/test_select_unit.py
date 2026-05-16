from sqlinpython import (
    NestedFromClause,
    Select,
    Subquery,
    TableFunctionRef,
    TableRef,
    literal,
)
from sqlinpython.base import SqlElement


def to_str(element: SqlElement) -> str:
    buffer: list[str] = []
    element._create_query(buffer)
    return "".join(buffer)


# ---------------------------------------------------------------------------
# TableRef
# ---------------------------------------------------------------------------


def test_table_ref_simple() -> None:
    assert to_str(TableRef("users")) == "users"


def test_table_ref_schema() -> None:
    assert to_str(TableRef("main", "users")) == "main.users"


def test_table_ref_aliased() -> None:
    assert to_str(TableRef("users").As("u")) == "users AS u"


def test_table_ref_indexed_by() -> None:
    assert (
        to_str(TableRef("users").IndexedBy("idx_name")) == "users INDEXED BY idx_name"
    )


def test_table_ref_not_indexed() -> None:
    assert to_str(TableRef("users").NotIndexed) == "users NOT INDEXED"


def test_table_star_result_column() -> None:
    assert to_str(TableRef("users").Star) == "users.*"


def test_table_column_simple() -> None:
    assert to_str(TableRef("users")["id"]) == "users.id"


def test_table_column_aliased() -> None:
    assert to_str(TableRef("users").As("u")["id"]) == "u.id"


def test_table_column_schema_qualified() -> None:
    assert to_str(TableRef("main", "users")["id"]) == "main.users.id"


# ---------------------------------------------------------------------------
# TableFunctionRef
# ---------------------------------------------------------------------------


def test_table_function_ref() -> None:
    f = TableFunctionRef("json_each")(literal("[]"))
    assert to_str(f) == 'json_each("[]")'


def test_table_function_ref_aliased() -> None:
    f = TableFunctionRef("schema", "json_each")(literal("[]")).As("j")
    assert to_str(f) == 'schema.json_each("[]") AS j'


# ---------------------------------------------------------------------------
# Subquery
# ---------------------------------------------------------------------------


def test_subquery() -> None:
    inner = Select("*").From(TableRef("t"))
    assert to_str(Subquery(inner)) == "(SELECT * FROM t)"


def test_subquery_aliased() -> None:
    inner = Select("*").From(TableRef("t"))
    assert to_str(Subquery(inner).As("s")) == "(SELECT * FROM t) AS s"


# ---------------------------------------------------------------------------
# NestedFromClause
# ---------------------------------------------------------------------------


def test_nested_from_clause_tables() -> None:
    n = NestedFromClause((TableRef("a"), TableRef("b")))
    assert to_str(n) == "(a, b)"


def test_nested_from_clause_join() -> None:
    join = TableRef("a").Join(TableRef("b")).On(literal(1))
    assert to_str(NestedFromClause(join)) == "(a JOIN b ON 1)"


# ---------------------------------------------------------------------------
# Join types
# ---------------------------------------------------------------------------


def test_join_on() -> None:
    assert to_str(TableRef("a").Join(TableRef("b")).On(literal(1))) == "a JOIN b ON 1"


def test_join_using() -> None:
    assert (
        to_str(TableRef("a").Join(TableRef("b")).Using("id")) == "a JOIN b USING (id)"
    )


def test_left_join() -> None:
    assert (
        to_str(TableRef("a").LeftJoin(TableRef("b")).On(literal(1)))
        == "a LEFT JOIN b ON 1"
    )


def test_left_outer_join() -> None:
    j = TableRef("a").LeftOuterJoin(TableRef("b")).On(literal(1))
    assert to_str(j) == "a LEFT OUTER JOIN b ON 1"


def test_right_join() -> None:
    assert (
        to_str(TableRef("a").RightJoin(TableRef("b")).On(literal(1)))
        == "a RIGHT JOIN b ON 1"
    )


def test_right_outer_join() -> None:
    j = TableRef("a").RightOuterJoin(TableRef("b")).On(literal(1))
    assert to_str(j) == "a RIGHT OUTER JOIN b ON 1"


def test_full_join() -> None:
    assert (
        to_str(TableRef("a").FullJoin(TableRef("b")).On(literal(1)))
        == "a FULL JOIN b ON 1"
    )


def test_full_outer_join() -> None:
    j = TableRef("a").FullOuterJoin(TableRef("b")).On(literal(1))
    assert to_str(j) == "a FULL OUTER JOIN b ON 1"


def test_inner_join() -> None:
    assert (
        to_str(TableRef("a").InnerJoin(TableRef("b")).On(literal(1)))
        == "a INNER JOIN b ON 1"
    )


def test_cross_join() -> None:
    assert (
        to_str(TableRef("a").CrossJoin(TableRef("b")).On(literal(1)))
        == "a CROSS JOIN b ON 1"
    )


def test_natural_join() -> None:
    assert to_str(TableRef("a").NaturalJoin(TableRef("b"))) == "a NATURAL JOIN b"


def test_natural_left_join() -> None:
    assert (
        to_str(TableRef("a").NaturalLeftJoin(TableRef("b"))) == "a NATURAL LEFT JOIN b"
    )


def test_natural_left_outer_join() -> None:
    j = TableRef("a").NaturalLeftOuterJoin(TableRef("b"))
    assert to_str(j) == "a NATURAL LEFT OUTER JOIN b"


def test_natural_right_join() -> None:
    assert (
        to_str(TableRef("a").NaturalRightJoin(TableRef("b")))
        == "a NATURAL RIGHT JOIN b"
    )


def test_natural_right_outer_join() -> None:
    j = TableRef("a").NaturalRightOuterJoin(TableRef("b"))
    assert to_str(j) == "a NATURAL RIGHT OUTER JOIN b"


def test_natural_full_join() -> None:
    assert (
        to_str(TableRef("a").NaturalFullJoin(TableRef("b"))) == "a NATURAL FULL JOIN b"
    )


def test_natural_full_outer_join() -> None:
    j = TableRef("a").NaturalFullOuterJoin(TableRef("b"))
    assert to_str(j) == "a NATURAL FULL OUTER JOIN b"


def test_natural_inner_join() -> None:
    assert (
        to_str(TableRef("a").NaturalInnerJoin(TableRef("b")))
        == "a NATURAL INNER JOIN b"
    )


def test_chained_joins() -> None:
    j = (
        TableRef("a")
        .Join(TableRef("b"))
        .On(literal(1))
        .LeftJoin(TableRef("c"))
        .On(literal(2))
    )
    assert to_str(j) == "a JOIN b ON 1 LEFT JOIN c ON 2"
