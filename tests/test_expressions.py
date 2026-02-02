from sqlinpython import expression as expr
from sqlinpython.base import SqlElement
from sqlinpython.name import Name


def to_str(element: SqlElement) -> str:
    buffer: list[str] = []
    element._create_query(buffer)
    return "".join(buffer)


def test_literal() -> None:
    assert to_str(expr.literal(1.0)) == "1.0"
    assert to_str(expr.literal(1)) == "1"
    assert to_str(expr.literal("hello")) == '"hello"'
    assert to_str(expr.literal(None)) == "NULL"
    assert to_str(expr.literal(True)) == "TRUE"
    assert to_str(expr.literal(False)) == "FALSE"
    assert to_str(expr.CurrentDate) == "CURRENT_DATE"
    assert to_str(expr.CurrentTime) == "CURRENT_TIME"
    assert to_str(expr.CurrentTimestamp) == "CURRENT_TIMESTAMP"


def test_or_and_operator() -> None:
    t = expr.literal(True)
    f = expr.literal(False)
    assert to_str(t.Or(f)) == "TRUE OR FALSE"
    assert to_str(t.Or(f).Or(t)) == "TRUE OR FALSE OR TRUE"
    assert to_str(t.Or(f).And(t)) == "(TRUE OR FALSE) AND TRUE"

    assert to_str(t.And(f)) == "TRUE AND FALSE"
    assert to_str(t.And(f).And(t)) == "TRUE AND FALSE AND TRUE"
    assert to_str(t.And(f).Or(t)) == "TRUE AND FALSE OR TRUE"


def test_not() -> None:
    t = expr.literal(True)
    f = expr.literal(False)
    assert to_str(expr.Not(f)) == "NOT FALSE"
    assert to_str(t.Is(expr.Not(f))) == "TRUE IS (NOT FALSE)"


def test_is_operator() -> None:
    t = expr.literal(True)
    f = expr.literal(False)
    n = expr.literal(None)
    assert to_str(t.Is(f)) == "TRUE IS FALSE"
    assert to_str(n.Is(n)) == "NULL IS NULL"
    assert to_str(t.Is.Not(f)) == "TRUE IS NOT FALSE"
    assert to_str(t.Is.DistinctFrom(f)) == "TRUE IS DISTINCT FROM FALSE"
    assert to_str(t.Is.Not.DistinctFrom(f)) == "TRUE IS NOT DISTINCT FROM FALSE"


def test_eq() -> None:
    t = expr.literal(True)
    f = expr.literal(False)
    assert to_str(t.eq(f, double_eq=False)) == "TRUE = FALSE"
    assert to_str(t.eq(f, double_eq=True)) == "TRUE == FALSE"
    assert to_str(t.ne(f, arrows=True)) == "TRUE <> FALSE"
    assert to_str(t.ne(f, arrows=False)) == "TRUE != FALSE"


def test_auto_parentheses() -> None:
    t = expr.literal(True)
    f = expr.literal(False)
    assert to_str(expr.Not(t.Or(f).And(t))) == "NOT ((TRUE OR FALSE) AND TRUE)"
    assert to_str(expr.Not(t).And(f).Or(t)) == "NOT TRUE AND FALSE OR TRUE"


def test_in() -> None:
    t = expr.literal(True)
    f = expr.literal(False)
    assert to_str(t.In()) == "TRUE IN ()"
    assert to_str(t.In(t, f)) == "TRUE IN (TRUE, FALSE)"
    # TODO: SelectStatement
    assert to_str(t.In(Name("a"))) == "TRUE IN a"
    assert to_str(t.In(Name('a"'))) == 'TRUE IN "a"""'
    assert to_str(t.In(Name("a"), Name("b"))) == "TRUE IN a.b"
    assert to_str(t.In(Name('a"'), Name('b"'))) == 'TRUE IN "a"""."b"""'
    # TODO: TableFunction

    assert to_str(t.Not.In()) == "TRUE NOT IN ()"
    assert to_str(t.Not.In(t, f)) == "TRUE NOT IN (TRUE, FALSE)"
    # TODO: SelectStatement
    assert to_str(t.Not.In(Name("a"))) == "TRUE NOT IN a"
    assert to_str(t.Not.In(Name('a"'))) == 'TRUE NOT IN "a"""'
    assert to_str(t.Not.In(Name("a"), Name("b"))) == "TRUE NOT IN a.b"
    assert to_str(t.Not.In(Name('a"'), Name('b"'))) == 'TRUE NOT IN "a"""."b"""'
    # TODO: TableFunction

    assert to_str(expr.Not(t).In()) == "(NOT TRUE) IN ()"


def test_like_likes() -> None:
    t = expr.literal(True)
    f = expr.literal(False)
    assert to_str(t.Like(f)) == "TRUE LIKE FALSE"
    assert to_str(t.Not.Like(f)) == "TRUE NOT LIKE FALSE"
    assert to_str(t.Like(expr.Not(f))) == "TRUE LIKE (NOT FALSE)"
    assert to_str(t.Like(f).Escape(t)) == "TRUE LIKE FALSE ESCAPE TRUE"
    assert to_str(t.Like(expr.Not(f)).Escape(t)) == "TRUE LIKE (NOT FALSE) ESCAPE TRUE"
    assert to_str(t.Glob(f)) == "TRUE GLOB FALSE"
    assert to_str(t.Not.Glob(f)) == "TRUE NOT GLOB FALSE"
    assert to_str(t.Glob(expr.Not(f))) == "TRUE GLOB (NOT FALSE)"
    assert to_str(t.Regexp(f)) == "TRUE REGEXP FALSE"
    assert to_str(t.Not.Regexp(f)) == "TRUE NOT REGEXP FALSE"
    assert to_str(t.Regexp(expr.Not(f))) == "TRUE REGEXP (NOT FALSE)"
    assert to_str(t.Match(f)) == "TRUE MATCH FALSE"
    assert to_str(t.Not.Match(f)) == "TRUE NOT MATCH FALSE"
    assert to_str(t.Match(expr.Not(f))) == "TRUE MATCH (NOT FALSE)"


def test_null_compare() -> None:
    t = expr.literal(True)
    assert to_str(t.IsNull) == "TRUE ISNULL"
    assert to_str(t.NotNull) == "TRUE NOTNULL"
    assert to_str(t.Not.Null) == "TRUE NOT NULL"


def test_comparison() -> None:
    a = expr.literal(1)
    b = expr.literal(2)
    assert to_str(a < b) == "1 < 2"
    assert to_str(a < b + a) == "1 < 2 + 1"
    assert to_str((a < b) + a) == "(1 < 2) + 1"
    assert to_str(a <= b) == "1 <= 2"
    assert to_str(a - b <= a) == "1 - 2 <= 1"
    assert to_str(a - (b <= a)) == "1 - (2 <= 1)"
    assert to_str(a > b) == "1 > 2"
    assert to_str(a > b - a) == "1 > 2 - 1"
    assert to_str((a > b) - a) == "(1 > 2) - 1"
    assert to_str(a >= b) == "1 >= 2"
    assert to_str(a + b >= a) == "1 + 2 >= 1"
    assert to_str(a + (b >= a)) == "1 + (2 >= 1)"


def test_arithmetic() -> None:
    a = expr.literal(1)
    b = expr.literal(2)
    assert to_str(a + b) == "1 + 2"
    assert to_str(a + b + a) == "1 + 2 + 1"
    assert to_str(a + (b + a)) == "1 + (2 + 1)"
    assert to_str(a - b) == "1 - 2"
    assert to_str(a - b - a) == "1 - 2 - 1"
    assert to_str(a - (b - a)) == "1 - (2 - 1)"
    assert to_str(a * b) == "1 * 2"
    assert to_str(a * b * a) == "1 * 2 * 1"
    assert to_str(a * (b * a)) == "1 * (2 * 1)"
    assert to_str(a / b) == "1 / 2"
    assert to_str(a / b / a) == "1 / 2 / 1"
    assert to_str(a / (b / a)) == "1 / (2 / 1)"
    assert to_str(a % b) == "1 % 2"
    assert to_str(a % b % a) == "1 % 2 % 1"
    assert to_str(a % (b % a)) == "1 % (2 % 1)"
    assert to_str(a + b * a) == "1 + 2 * 1"
    assert to_str((a + b) * a) == "(1 + 2) * 1"
    assert to_str(a + b / a + b) == "1 + 2 / 1 + 2"
    assert to_str((a + b) * (a - b)) == "(1 + 2) * (1 - 2)"


def test_concat_like() -> None:
    a = expr.literal("a")
    b = expr.literal("b")
    assert to_str(a.Concat(b)) == '"a" || "b"'
    assert to_str(a.Concat(b).Concat(a)) == '"a" || "b" || "a"'
    assert to_str(a.Concat(b.Concat(a))) == '"a" || ("b" || "a")'
    assert to_str(a.Extract(b)) == '"a" -> "b"'
    assert to_str(a.Extract(b).Extract(a)) == '"a" -> "b" -> "a"'
    assert to_str(a.Extract(b.Extract(a))) == '"a" -> ("b" -> "a")'
    assert to_str(a.Extract2(b)) == '"a" ->> "b"'
    assert to_str(a.Extract2(b).Extract(a)) == '"a" ->> "b" -> "a"'
    assert to_str(a.Extract(b.Extract2(a))) == '"a" -> ("b" ->> "a")'


def test_unary_operators() -> None:
    a = expr.literal(1)
    b = expr.literal(2)
    assert to_str(-a) == "-1"
    assert to_str(+a) == "+1"
    assert to_str(~a) == "~1"
    assert to_str(-b + a) == "-2 + 1"
    assert to_str(a + (+b)) == "1 + +2"
    assert to_str(~b + a) == "~2 + 1"
