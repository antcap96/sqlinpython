from sqlinpython import Delete, Select, TableName, With
from sqlinpython import expression as expr
from sqlinpython.delete import DeleteStatement, DeleteStatementLimited


def test_with_delete() -> None:
    q = With(TableName("cte").As(Select(expr.literal(1)))).Delete.From("users")
    assert isinstance(q, DeleteStatement)
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "WITH cte AS (SELECT 1) DELETE FROM users"


def test_with_recursive_delete() -> None:
    q = With.Recursive(
        TableName("cte1").As(Select(expr.literal(1))),
        TableName("cte2").As(Select(expr.literal(2))),
    ).Delete.From("users")
    assert isinstance(q, DeleteStatement)
    assert isinstance(q, DeleteStatementLimited)
    assert (
        q.get_query()
        == "WITH RECURSIVE cte1 AS (SELECT 1), cte2 AS (SELECT 2) DELETE FROM users"
    )


def test_delete() -> None:
    q = Delete.From("users")
    assert isinstance(q, DeleteStatement)
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "DELETE FROM users"


def test_delete_schema_qualified() -> None:
    q = Delete.From("main", "users")
    assert isinstance(q, DeleteStatement)
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "DELETE FROM main.users"


def test_delete_where() -> None:
    q = Delete.From("users").Where(expr.literal(1))
    assert isinstance(q, DeleteStatement)
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "DELETE FROM users WHERE 1"


def test_delete_as() -> None:
    q = Delete.From("users").As("u")
    assert isinstance(q, DeleteStatement)
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "DELETE FROM users AS u"


def test_delete_indexed() -> None:
    q = Delete.From("users").IndexedBy("idx_users")
    assert isinstance(q, DeleteStatement)
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "DELETE FROM users INDEXED BY idx_users"


def test_delete_indexed_where() -> None:
    q = Delete.From("users").IndexedBy("idx_users").Where(expr.literal(1))
    assert isinstance(q, DeleteStatement)
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "DELETE FROM users INDEXED BY idx_users WHERE 1"


def test_delete_not_indexed() -> None:
    q = Delete.From("users").NotIndexed
    assert isinstance(q, DeleteStatement)
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "DELETE FROM users NOT INDEXED"


def test_delete_as_not_indexed() -> None:
    q = Delete.From("users").As("u").NotIndexed
    assert isinstance(q, DeleteStatement)
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "DELETE FROM users AS u NOT INDEXED"


def test_delete_as_where() -> None:
    q = Delete.From("users").As("u").Where(expr.literal(1))
    assert isinstance(q, DeleteStatement)
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "DELETE FROM users AS u WHERE 1"


def test_delete_returning_clause() -> None:
    q = Delete.From("users").Returning(expr.literal(1))
    assert isinstance(q, DeleteStatement)
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "DELETE FROM users RETURNING 1"


def test_delete_where_returning() -> None:
    q = Delete.From("users").Where(expr.literal(1)).Returning("*")
    assert isinstance(q, DeleteStatement)
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "DELETE FROM users WHERE 1 RETURNING *"


def test_delete_returning_clause_star() -> None:
    q = Delete.From("users").Returning("*")
    assert isinstance(q, DeleteStatement)
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "DELETE FROM users RETURNING *"


def test_delete_returning_clause_as() -> None:
    q = Delete.From("users").Returning(
        expr.literal(1).As("result"), expr.literal(2).As("other_result")
    )
    assert isinstance(q, DeleteStatement)
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "DELETE FROM users RETURNING 1 AS result, 2 AS other_result"


def test_delete_limited_order_by_1() -> None:
    q = Delete.From("users").OrderBy(expr.literal(1))
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "DELETE FROM users ORDER BY 1"


def test_delete_limited_order_by_2() -> None:
    q = Delete.From("users").OrderBy(expr.literal(1), expr.literal(2).Asc)
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "DELETE FROM users ORDER BY 1, 2 ASC"


def test_delete_limited_limit_1() -> None:
    q = Delete.From("users").Limit(expr.literal(1))
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "DELETE FROM users LIMIT 1"


def test_delete_limited_limit_2() -> None:
    q = Delete.From("users").Limit(expr.literal(1), expr.literal(2))
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "DELETE FROM users LIMIT 1, 2"


def test_delete_limited_limit_offset() -> None:
    q = Delete.From("users").Limit(expr.literal(1)).Offset(expr.literal(2))
    assert isinstance(q, DeleteStatementLimited)
    assert q.get_query() == "DELETE FROM users LIMIT 1 OFFSET 2"


def test_delete_limited_empty_order_by_fails_type_check() -> None:
    Delete.From("users").OrderBy()  # type: ignore[call-arg] # pyright: ignore[reportCallIssue]
    # ty doesn't currently identify this error -ty: ignore[missing-argument]


def test_delete_limited_full_chain() -> None:
    q = (
        With(TableName("cte").As(Select(expr.literal(1))))
        .Delete.From("users")
        .As("u")
        .Where(expr.literal(1))
        .Returning("*")
        .OrderBy(expr.literal(1))
        .Limit(expr.literal(1))
    )
    assert isinstance(q, DeleteStatementLimited)
    assert (
        q.get_query()
        == "WITH cte AS (SELECT 1) "
        + "DELETE FROM users AS u "
        + "WHERE 1 "
        + "RETURNING * "
        + "ORDER BY 1 "
        + "LIMIT 1"
    )
