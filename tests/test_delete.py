from sqlinpython import Delete, Select, TableName, With
from sqlinpython import expression as expr


def test_with_delete() -> None:
    q = With(TableName("cte").As(Select(expr.literal(1)))).Delete.From("users")
    assert q.get_query() == "WITH cte AS (SELECT 1) DELETE FROM users"


def test_with_recursive_delete() -> None:
    q = With.Recursive(
        TableName("cte1").As(Select(expr.literal(1))),
        TableName("cte2").As(Select(expr.literal(2))),
    ).Delete.From("users")
    assert (
        q.get_query()
        == "WITH RECURSIVE cte1 AS (SELECT 1), cte2 AS (SELECT 2) DELETE FROM users"
    )


def test_delete() -> None:
    q = Delete.From("users")
    assert q.get_query() == "DELETE FROM users"


def test_delete_schema_qualified() -> None:
    q = Delete.From("main", "users")
    assert q.get_query() == "DELETE FROM main.users"


def test_delete_where() -> None:
    q = Delete.From("users").Where(expr.literal(1))
    assert q.get_query() == "DELETE FROM users WHERE 1"


def test_delete_as() -> None:
    q = Delete.From("users").As("u")
    assert q.get_query() == "DELETE FROM users AS u"


def test_delete_indexed() -> None:
    q = Delete.From("users").IndexedBy("idx_users")
    assert q.get_query() == "DELETE FROM users INDEXED BY idx_users"


def test_delete_indexed_where() -> None:
    q = Delete.From("users").IndexedBy("idx_users").Where(expr.literal(1))
    assert q.get_query() == "DELETE FROM users INDEXED BY idx_users WHERE 1"


def test_delete_not_indexed() -> None:
    q = Delete.From("users").NotIndexed
    assert q.get_query() == "DELETE FROM users NOT INDEXED"


def test_delete_as_not_indexed() -> None:
    q = Delete.From("users").As("u").NotIndexed
    assert q.get_query() == "DELETE FROM users AS u NOT INDEXED"


def test_delete_as_where() -> None:
    q = Delete.From("users").As("u").Where(expr.literal(1))
    assert q.get_query() == "DELETE FROM users AS u WHERE 1"


def test_delete_returning_clause() -> None:
    q = Delete.From("users").Returning(expr.literal(1))
    assert q.get_query() == "DELETE FROM users RETURNING 1"


def test_delete_where_returning() -> None:
    q = Delete.From("users").Where(expr.literal(1)).Returning("*")
    assert q.get_query() == "DELETE FROM users WHERE 1 RETURNING *"


def test_delete_returning_clause_star() -> None:
    q = Delete.From("users").Returning("*")
    assert q.get_query() == "DELETE FROM users RETURNING *"


def test_delete_returning_clause_as() -> None:
    q = Delete.From("users").Returning(
        expr.literal(1).As("result"), expr.literal(2).As("other_result")
    )
    assert q.get_query() == "DELETE FROM users RETURNING 1 AS result, 2 AS other_result"
