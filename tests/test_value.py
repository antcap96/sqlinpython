from sqlinpython.column_def import ColumnRef
from sqlinpython.value import Select, Value, Any, All


def test_factor_1() -> None:
    assert (ColumnRef("c") * ColumnRef("d"))._create_query() == "c * d"


def test_factor_2() -> None:
    assert (ColumnRef("e") / Value(5))._create_query() == "e / 5"


def test_factor_3() -> None:
    assert (ColumnRef("f") % Value(10))._create_query() == "f % 10"


def test_summand_1() -> None:
    assert (ColumnRef("a") + ColumnRef("b"))._create_query() == "a + b"


def test_summand_2() -> None:
    assert (ColumnRef("a") - ColumnRef("b"))._create_query() == "a - b"


def test_operand_1() -> None:
    assert (Value("foo").strcat(ColumnRef("s")))._create_query() == "'foo' || s"


def test_rhs_operand_1() -> None:
    assert ColumnRef("s", "my_col")._create_query() == "s.my_col"


def test_rhs_operand_2() -> None:
    assert Any(ColumnRef("my_col") + Value(1))._create_query() == "ANY(my_col + 1)"


def test_rhs_operand_3() -> None:
    assert (
        All(Select("select foo from bar where bas > 5"))._create_query()
        == "ALL(select foo from bar where bas > 5)"
    )


def test_condition_1() -> None:
    assert (ColumnRef("FOO").eq(Value("bar")))._create_query() == "FOO = 'bar'"


def test_condition_2() -> None:
    assert (ColumnRef("NAME").Like(Value("Jo%")))._create_query() == "NAME LIKE 'Jo%'"


def test_condition_3() -> None:
    assert (
        ColumnRef("ID").In(Value(1), Value(2), Value(3))
    )._create_query() == "ID IN (1, 2, 3)"


def test_condition_4() -> None:
    assert (
        ColumnRef("ID").NotExists(Select("SELECT 1 FROM FOO WHERE BAR < 10"))
    )._create_query() == "ID NOT EXISTS (SELECT 1 FROM FOO WHERE BAR < 10)"


def test_condition_5() -> None:
    assert (
        ColumnRef("N").Between(Value(1), Value(100))
    )._create_query() == "N BETWEEN 1 AND 100"


def test_boolean_condition_1() -> None:
    assert (ColumnRef("N").eq(Value(1)))._create_query() == "N = 1"


def test_boolean_condition_2() -> None:
    assert (~ColumnRef("N").eq(Value(1)))._create_query() == "NOT N = 1"


def test_and_condition_1() -> None:
    assert (
        ColumnRef("FOO")
        .ne(Value("bar"))
        .And(ColumnRef("ID").eq(Value(1)))
        ._create_query()
        == "FOO <> 'bar' AND ID = 1"
    )


def test_expression_1() -> None:
    assert (
        ColumnRef("ID")
        .eq(Value(1))
        .Or(ColumnRef("NAME").eq(Value("Hi")))
        ._create_query()
        == "ID = 1 OR NAME = 'Hi'"
    )


def test_complex_expression_1() -> None:
    assert ((ColumnRef("x") + Value(1)) * Value(-1))._create_query() == "(x + 1) * -1"
    assert ((ColumnRef("x") * Value(1)) + Value(-1))._create_query() == "x * 1 + -1"


def test_complex_expression_2() -> None:
    x = ColumnRef("x")
    assert x.And(x.Or(x.And(x)))._create_query() == "x AND (x OR x AND x)"


def test_complex_expression_3() -> None:
    x = ColumnRef("x")
    assert (
        x.Between(x.And(x), x.Or(x))._create_query()
        == "x BETWEEN (x AND x) AND (x OR x)"
    )


def test_complex_expression_4() -> None:
    x = ColumnRef("x")
    assert (
        x + x * x % x - x * x / x - x
    )._create_query() == "x + x * x % x - x * x / x - x"
    assert (
        x + x * (x % x) - x * (x / x) - x
    )._create_query() == "x + x * (x % x) - x * (x / x) - x"
    assert (
        x + x * (x % x - x * x / x) - x
    )._create_query() == "x + x * (x % x - x * x / x) - x"
    assert (
        x + x * (x % (x - x) * x / x) - x
    )._create_query() == "x + x * (x % (x - x) * x / x) - x"
    assert (x.strcat(x).strcat(x).strcat(x))._create_query() == "x || x || x || x"
    assert (x.strcat(x.strcat(x).strcat(x)))._create_query() == "x || (x || x || x)"
    assert (x + x.strcat(x))._create_query() == "x + (x || x)"
    assert (x * x.strcat(x))._create_query() == "x * (x || x)"
    assert ((x * x).strcat(x))._create_query() == "x * x || x"
    assert ((x + x).strcat(x))._create_query() == "x + x || x"
    assert (x.Or(x).Or(x))._create_query() == "x OR x OR x"
    assert (x.And(x).And(x))._create_query() == "x AND x AND x"
