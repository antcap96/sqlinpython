from sqlinpython import expression as expr


def test_literal() -> None:
    assert expr.Literal(1.0)._create_query() == "1.0"
    assert expr.Literal(1)._create_query() == "1"
    assert expr.Literal("hello")._create_query() == '"hello"'
    assert expr.Literal(None)._create_query() == "NULL"
    assert expr.Literal(True)._create_query() == "TRUE"
    assert expr.Literal(False)._create_query() == "FALSE"


def test_or_and_operator() -> None:
    t = expr.Literal(True)
    f = expr.Literal(False)
    assert t.Or(f)._create_query() == "TRUE OR FALSE"
    assert t.Or(f).Or(t)._create_query() == "TRUE OR FALSE OR TRUE"
    assert t.Or(f).And(t)._create_query() == "(TRUE OR FALSE) AND TRUE"

    assert t.And(f)._create_query() == "TRUE AND FALSE"
    assert t.And(f).And(t)._create_query() == "TRUE AND FALSE AND TRUE"
    assert t.And(f).Or(t)._create_query() == "TRUE AND FALSE OR TRUE"


def test_not() -> None:
    t = expr.Literal(True)
    f = expr.Literal(False)
    assert expr.Not(f)._create_query() == "NOT FALSE"
    assert t.Is(expr.Not(f))._create_query() == "TRUE IS (NOT FALSE)"


def test_is_operator() -> None:
    t = expr.Literal(True)
    f = expr.Literal(False)
    n = expr.Literal(None)
    assert t.Is(f)._create_query() == "TRUE IS FALSE"
    assert n.Is(n)._create_query() == "NULL IS NULL"
    assert t.Is.Not(f)._create_query() == "TRUE IS NOT FALSE"
    assert t.Is.DistinctFrom(f)._create_query() == "TRUE IS DISTINCT FROM FALSE"
    assert t.Is.Not.DistinctFrom(f)._create_query() == "TRUE IS NOT DISTINCT FROM FALSE"


def test_eq() -> None:
    t = expr.Literal(True)
    f = expr.Literal(False)
    assert t.eq(f, double_eq=False)._create_query() == "TRUE = FALSE"
    assert t.eq(f, double_eq=True)._create_query() == "TRUE == FALSE"
    assert t.ne(f, arrows=True)._create_query() == "TRUE <> FALSE"
    assert t.ne(f, arrows=False)._create_query() == "TRUE != FALSE"


def test_auto_parentheses() -> None:
    t = expr.Literal(True)
    f = expr.Literal(False)
    assert expr.Not(t.Or(f).And(t))._create_query() == "NOT ((TRUE OR FALSE) AND TRUE)"
    assert expr.Not(t).And(f).Or(t)._create_query() == "NOT TRUE AND FALSE OR TRUE"
