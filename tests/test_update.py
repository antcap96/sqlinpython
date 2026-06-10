import pytest

from sqlinpython import (
    Name,
    Select,
    TableName,
    TableRef,
    Update,
    UpdateStatement,
    UpdateStatementLimited,
    With,
    literal,
)


def test_with_update() -> None:
    q = (
        With(TableName("cte").As(Select(literal(1))))
        .Update("users")
        .Set(column=literal(1))
    )
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "WITH cte AS (SELECT 1) UPDATE users SET column = 1"


def test_with_recursive_update() -> None:
    q = (
        With.Recursive(
            TableName("cte1").As(Select(literal(1))),
            TableName("cte2").As(Select(literal(2))),
        )
        .Update("users")
        .Set(column=literal(1))
    )
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert (
        q.get_query()
        == "WITH RECURSIVE cte1 AS (SELECT 1), cte2 AS (SELECT 2) UPDATE users SET column = 1"
    )


def test_update() -> None:
    q = Update("users").Set(column=literal(1))
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET column = 1"


def test_update_schema_qualified() -> None:
    q = Update("main", "users").Set(column=literal(1))
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE main.users SET column = 1"


def test_update_2() -> None:
    q = Update("users").Set(column=literal(1), other=literal(2))
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET column = 1, other = 2"


def test_update_dict_str() -> None:
    q = Update("users").Set({"column": literal(1), "other": literal(2)})
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET column = 1, other = 2"


def test_update_dict_mixed() -> None:
    q = Update("users").Set({"column": literal(1), Name("other"): literal(2)})
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET column = 1, other = 2"


def test_update_dict_list_str() -> None:
    q = Update("users").Set({("column", "other"): literal(1)})
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET (column, other) = 1"


def test_update_dict_list_mixed() -> None:
    q = Update("users").Set({("column", Name("other")): literal(1)})
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET (column, other) = 1"


def test_update_dict_list_mixed_2() -> None:
    q = Update("users").Set(
        {("column", Name("other")): literal(1), "another": literal(2)}
    )
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET (column, other) = 1, another = 2"


def test_update_or_abort() -> None:
    q = Update.OrAbort("users").Set(column=literal(1))
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE OR ABORT users SET column = 1"


def test_update_or_fail() -> None:
    q = Update.OrFail("users").Set(column=literal(1))
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE OR FAIL users SET column = 1"


def test_update_or_ignore() -> None:
    q = Update.OrIgnore("users").Set(column=literal(1))
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE OR IGNORE users SET column = 1"


def test_update_or_replace() -> None:
    q = Update.OrReplace("users").Set(column=literal(1))
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE OR REPLACE users SET column = 1"


def test_update_or_rollback() -> None:
    q = Update.OrRollback("users").Set(column=literal(1))
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE OR ROLLBACK users SET column = 1"


def test_update_as() -> None:
    q = Update("users").As("u").Set(column=literal(1))
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users AS u SET column = 1"


def test_update_indexed_by() -> None:
    q = Update("users").IndexedBy("idx_users").Set(column=literal(1))
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users INDEXED BY idx_users SET column = 1"


def test_update_not_indexed() -> None:
    q = Update("users").NotIndexed.Set(column=literal(1))
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users NOT INDEXED SET column = 1"


def test_update_set_from() -> None:
    q = Update("users").Set(column=literal(1)).From(TableRef("table"))
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET column = 1 FROM table"


def test_update_set_from_join() -> None:
    q = (
        Update("users")
        .Set(column=literal(1))
        .From(TableRef("table").Join(TableRef("other")))
    )
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET column = 1 FROM table JOIN other"


def test_update_set_from_comma() -> None:
    q = (
        Update("users")
        .Set(column=literal(1))
        .From(TableRef("table"), TableRef("other"))
    )
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET column = 1 FROM table, other"


def test_update_where() -> None:
    q = Update("users").Set(column=literal(1)).Where(literal(1))
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET column = 1 WHERE 1"


def test_update_returning() -> None:
    q = Update("users").Set(column=literal(1)).Returning(literal(1))
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET column = 1 RETURNING 1"


def test_update_returning_as() -> None:
    q = Update("users").Set(column=literal(1)).Returning(literal(1).As("alias"))
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET column = 1 RETURNING 1 AS alias"


def test_update_where_returning() -> None:
    q = Update("users").Set(column=literal(1)).Where(literal(1)).Returning("*")
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET column = 1 WHERE 1 RETURNING *"


def test_update_set_from_returning() -> None:
    q = Update("users").Set(column=literal(1)).From(TableRef("other")).Returning("*")
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET column = 1 FROM other RETURNING *"


def test_update_schema_qualified_as() -> None:
    q = Update("main", "users").As("u").Set(column=literal(1))
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE main.users AS u SET column = 1"


def test_update_set_empty_raises() -> None:
    with pytest.raises(ValueError):
        _ = Update("users").Set()


def test_update_full_chain() -> None:
    q = (
        With(TableName("cte").As(Select(literal(1))))
        .Update.OrAbort("users")
        .As("u")
        .Set(column=literal(1))
        .From(TableRef("other"))
        .Where(literal(1))
        .Returning("*")
    )
    assert isinstance(q, UpdateStatement)
    assert isinstance(q, UpdateStatementLimited)
    assert (
        q.get_query()
        == "WITH cte AS (SELECT 1) UPDATE OR ABORT users AS u SET column = 1 FROM other WHERE 1 RETURNING *"
    )


def test_update_limited_empty_order_by_fails_type_check() -> None:
    Update("users").Set(column=literal(1)).OrderBy()  # type: ignore[call-arg] # pyright: ignore[reportCallIssue]
    # ty doesn't currently identify this error -ty: ignore[missing-argument]


def test_update_limited_order_by_1() -> None:
    q = Update("users").Set(column=literal(1)).OrderBy(literal(1))
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET column = 1 ORDER BY 1"


def test_update_limited_order_by_2() -> None:
    q = Update("users").Set(column=literal(1)).OrderBy(literal(1), literal(2).Asc)
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET column = 1 ORDER BY 1, 2 ASC"


def test_update_limited_limit_1() -> None:
    q = Update("users").Set(column=literal(1)).Limit(literal(1))
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET column = 1 LIMIT 1"


def test_update_limited_limit_2() -> None:
    q = Update("users").Set(column=literal(1)).Limit(literal(1), literal(2))
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET column = 1 LIMIT 1, 2"


def test_update_limited_limit_offset() -> None:
    q = Update("users").Set(column=literal(1)).Limit(literal(1)).Offset(literal(2))
    assert isinstance(q, UpdateStatementLimited)
    assert q.get_query() == "UPDATE users SET column = 1 LIMIT 1 OFFSET 2"


def test_update_limited_full_chain() -> None:
    q = (
        With(TableName("cte").As(Select(literal(1))))
        .Update.OrAbort("users")
        .As("u")
        .Set(column=literal(1))
        .From(TableRef("other"))
        .Where(literal(1))
        .Returning("*")
        .OrderBy(literal(1))
        .Limit(literal(1))
    )
    assert isinstance(q, UpdateStatementLimited)
    assert (
        q.get_query()
        == "WITH cte AS (SELECT 1) "
        + "UPDATE OR ABORT users AS u "
        + "SET column = 1 "
        + "FROM other "
        + "WHERE 1 "
        + "RETURNING * "
        + "ORDER BY 1 "
        + "LIMIT 1"
    )


def test_update_where_accepts_python_literal() -> None:
    q = Update("users").Set(column=literal(1)).Where(1)
    assert q.get_query() == "UPDATE users SET column = 1 WHERE 1"


def test_update_limit_accepts_python_literal() -> None:
    q = Update("users").Set(column=literal(1)).Limit(1)
    assert q.get_query() == "UPDATE users SET column = 1 LIMIT 1"


def test_update_limit_comma_accepts_python_literals() -> None:
    q = Update("users").Set(column=literal(1)).Limit(1, 2)
    assert q.get_query() == "UPDATE users SET column = 1 LIMIT 1, 2"


def test_update_limit_offset_accepts_python_literals() -> None:
    q = Update("users").Set(column=literal(1)).Limit(1).Offset(2)
    assert q.get_query() == "UPDATE users SET column = 1 LIMIT 1 OFFSET 2"


def test_update_limit_offset_none_is_sql_null() -> None:
    q = Update("users").Set(column=literal(1)).Limit(1, None)
    assert q.get_query() == "UPDATE users SET column = 1 LIMIT 1, NULL"
