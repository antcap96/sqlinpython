from sqlinpython import Explain, Select, literal


def test_explain_select() -> None:
    assert Explain(Select(literal(1))).get_query() == "EXPLAIN SELECT 1"


def test_explain_query_plan_select() -> None:
    assert (
        Explain.QueryPlan(Select(literal(1))).get_query()
        == "EXPLAIN QUERY PLAN SELECT 1"
    )


def test_explain_cannot_wrap_explain() -> None:
    _ = Explain(Explain(Select(literal(1))))  # type: ignore[arg-type] # pyright: ignore[reportArgumentType] # ty: ignore[invalid-argument-type]
