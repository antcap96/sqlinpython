from sqlinpython import expression as expr
from sqlinpython.name import Name


def test_literal() -> None:
    assert expr.literal(1.0)._create_query() == "1.0"
    assert expr.literal(1)._create_query() == "1"
    assert expr.literal("hello")._create_query() == '"hello"'
    assert expr.literal(None)._create_query() == "NULL"
    assert expr.literal(True)._create_query() == "TRUE"
    assert expr.literal(False)._create_query() == "FALSE"
    assert expr.CurrentDate._create_query() == "CURRENT_DATE"
    assert expr.CurrentTime._create_query() == "CURRENT_TIME"
    assert expr.CurrentTimestamp._create_query() == "CURRENT_TIMESTAMP"


def test_or_and_operator() -> None:
    t = expr.literal(True)
    f = expr.literal(False)
    assert t.Or(f)._create_query() == "TRUE OR FALSE"
    assert t.Or(f).Or(t)._create_query() == "TRUE OR FALSE OR TRUE"
    assert t.Or(f).And(t)._create_query() == "(TRUE OR FALSE) AND TRUE"

    assert t.And(f)._create_query() == "TRUE AND FALSE"
    assert t.And(f).And(t)._create_query() == "TRUE AND FALSE AND TRUE"
    assert t.And(f).Or(t)._create_query() == "TRUE AND FALSE OR TRUE"


def test_not() -> None:
    t = expr.literal(True)
    f = expr.literal(False)
    assert expr.Not(f)._create_query() == "NOT FALSE"
    assert t.Is(expr.Not(f))._create_query() == "TRUE IS (NOT FALSE)"


def test_is_operator() -> None:
    t = expr.literal(True)
    f = expr.literal(False)
    n = expr.literal(None)
    assert t.Is(f)._create_query() == "TRUE IS FALSE"
    assert n.Is(n)._create_query() == "NULL IS NULL"
    assert t.Is.Not(f)._create_query() == "TRUE IS NOT FALSE"
    assert t.Is.DistinctFrom(f)._create_query() == "TRUE IS DISTINCT FROM FALSE"
    assert t.Is.Not.DistinctFrom(f)._create_query() == "TRUE IS NOT DISTINCT FROM FALSE"


def test_eq() -> None:
    t = expr.literal(True)
    f = expr.literal(False)
    assert t.eq(f, double_eq=False)._create_query() == "TRUE = FALSE"
    assert t.eq(f, double_eq=True)._create_query() == "TRUE == FALSE"
    assert t.ne(f, arrows=True)._create_query() == "TRUE <> FALSE"
    assert t.ne(f, arrows=False)._create_query() == "TRUE != FALSE"


def test_auto_parentheses() -> None:
    t = expr.literal(True)
    f = expr.literal(False)
    assert expr.Not(t.Or(f).And(t))._create_query() == "NOT ((TRUE OR FALSE) AND TRUE)"
    assert expr.Not(t).And(f).Or(t)._create_query() == "NOT TRUE AND FALSE OR TRUE"


def test_in() -> None:
    t = expr.literal(True)
    f = expr.literal(False)
    assert t.In()._create_query() == "TRUE IN ()"
    assert t.In(t, f)._create_query() == "TRUE IN (TRUE, FALSE)"
    # TODO: SelectStatement
    assert t.In(Name("a"))._create_query() == "TRUE IN a"
    assert t.In(Name('a"'))._create_query() == 'TRUE IN "a"""'
    assert t.In(Name("a"), Name("b"))._create_query() == "TRUE IN a.b"
    assert t.In(Name('a"'), Name('b"'))._create_query() == 'TRUE IN "a"""."b"""'
    # TODO: TableFunction

    assert t.Not.In()._create_query() == "TRUE NOT IN ()"
    assert t.Not.In(t, f)._create_query() == "TRUE NOT IN (TRUE, FALSE)"
    # TODO: SelectStatement
    assert t.Not.In(Name("a"))._create_query() == "TRUE NOT IN a"
    assert t.Not.In(Name('a"'))._create_query() == 'TRUE NOT IN "a"""'
    assert t.Not.In(Name("a"), Name("b"))._create_query() == "TRUE NOT IN a.b"
    assert t.Not.In(Name('a"'), Name('b"'))._create_query() == 'TRUE NOT IN "a"""."b"""'
    # TODO: TableFunction

    assert expr.Not(t).In()._create_query() == "(NOT TRUE) IN ()"


def test_like_likes() -> None:
    t = expr.literal(True)
    f = expr.literal(False)
    assert t.Like(f)._create_query() == "TRUE LIKE FALSE"
    assert t.Not.Like(f)._create_query() == "TRUE NOT LIKE FALSE"
    assert t.Like(expr.Not(f))._create_query() == "TRUE LIKE (NOT FALSE)"
    assert t.Like(f).Escape(t)._create_query() == "TRUE LIKE FALSE ESCAPE TRUE"
    assert (
        t.Like(expr.Not(f)).Escape(t)._create_query()
        == "TRUE LIKE (NOT FALSE) ESCAPE TRUE"
    )
    assert t.Glob(f)._create_query() == "TRUE GLOB FALSE"
    assert t.Not.Glob(f)._create_query() == "TRUE NOT GLOB FALSE"
    assert t.Glob(expr.Not(f))._create_query() == "TRUE GLOB (NOT FALSE)"
    assert t.Regexp(f)._create_query() == "TRUE REGEXP FALSE"
    assert t.Not.Regexp(f)._create_query() == "TRUE NOT REGEXP FALSE"
    assert t.Regexp(expr.Not(f))._create_query() == "TRUE REGEXP (NOT FALSE)"
    assert t.Match(f)._create_query() == "TRUE MATCH FALSE"
    assert t.Not.Match(f)._create_query() == "TRUE NOT MATCH FALSE"
    assert t.Match(expr.Not(f))._create_query() == "TRUE MATCH (NOT FALSE)"


def test_null_compare() -> None:
    t = expr.literal(True)
    assert t.IsNull._create_query() == "TRUE ISNULL"
    assert t.NotNull._create_query() == "TRUE NOTNULL"
    assert t.Not.Null._create_query() == "TRUE NOT NULL"


def test_comparison() -> None:
    a = expr.literal(1)
    b = expr.literal(2)
    assert (a < b)._create_query() == "1 < 2"
    assert (a < b + a)._create_query() == "1 < 2 + 1"
    assert ((a < b) + a)._create_query() == "(1 < 2) + 1"
    assert (a <= b)._create_query() == "1 <= 2"
    assert (a - b <= a)._create_query() == "1 - 2 <= 1"
    assert (a - (b <= a))._create_query() == "1 - (2 <= 1)"
    assert (a > b)._create_query() == "1 > 2"
    assert (a > b - a)._create_query() == "1 > 2 - 1"
    assert ((a > b) - a)._create_query() == "(1 > 2) - 1"
    assert (a >= b)._create_query() == "1 >= 2"
    assert (a + b >= a)._create_query() == "1 + 2 >= 1"
    assert (a + (b >= a))._create_query() == "1 + (2 >= 1)"


def test_arithmetic() -> None:
    a = expr.literal(1)
    b = expr.literal(2)
    assert (a + b)._create_query() == "1 + 2"
    assert (a + b + a)._create_query() == "1 + 2 + 1"
    assert (a + (b + a))._create_query() == "1 + (2 + 1)"
    assert (a - b)._create_query() == "1 - 2"
    assert (a - b - a)._create_query() == "1 - 2 - 1"
    assert (a - (b - a))._create_query() == "1 - (2 - 1)"
    assert (a * b)._create_query() == "1 * 2"
    assert (a * b * a)._create_query() == "1 * 2 * 1"
    assert (a * (b * a))._create_query() == "1 * (2 * 1)"
    assert (a / b)._create_query() == "1 / 2"
    assert (a / b / a)._create_query() == "1 / 2 / 1"
    assert (a / (b / a))._create_query() == "1 / (2 / 1)"
    assert (a % b)._create_query() == "1 % 2"
    assert (a % b % a)._create_query() == "1 % 2 % 1"
    assert (a % (b % a))._create_query() == "1 % (2 % 1)"
    assert (a + b * a)._create_query() == "1 + 2 * 1"
    assert ((a + b) * a)._create_query() == "(1 + 2) * 1"
    assert (a + b / a + b)._create_query() == "1 + 2 / 1 + 2"
    assert ((a + b) * (a - b))._create_query() == "(1 + 2) * (1 - 2)"


def test_concat_like() -> None:
    a = expr.literal("a")
    b = expr.literal("b")
    assert (a.Concat(b))._create_query() == '"a" || "b"'
    assert (a.Concat(b).Concat(a))._create_query() == '"a" || "b" || "a"'
    assert (a.Concat(b.Concat(a)))._create_query() == '"a" || ("b" || "a")'
    assert (a.Extract(b))._create_query() == '"a" -> "b"'
    assert (a.Extract(b).Extract(a))._create_query() == '"a" -> "b" -> "a"'
    assert (a.Extract(b.Extract(a)))._create_query() == '"a" -> ("b" -> "a")'
    assert (a.Extract2(b))._create_query() == '"a" ->> "b"'
    assert (a.Extract2(b).Extract(a))._create_query() == '"a" ->> "b" -> "a"'
    assert (a.Extract(b.Extract2(a)))._create_query() == '"a" -> ("b" ->> "a")'


def test_unary_operators() -> None:
    a = expr.literal(1)
    b = expr.literal(2)
    assert (-a)._create_query() == "-1"
    assert (+a)._create_query() == "+1"
    assert (~a)._create_query() == "~1"
    assert (-b + a)._create_query() == "-2 + 1"
    assert (a + (+b))._create_query() == "1 + +2"
    assert (~b + a)._create_query() == "~2 + 1"
