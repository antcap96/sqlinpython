from sqlinpython.expression import Case, literal
from sqlinpython.base import SqlElement


def to_str(element: SqlElement) -> str:
    buffer: list[str] = []
    element._create_query(buffer)
    return "".join(buffer)


def test_simple_case_end() -> None:
    expr = Case.When(literal(1)).Then(literal(2)).End
    assert to_str(expr) == "CASE WHEN 1 THEN 2 END"


def test_case_with_else_end() -> None:
    expr = Case.When(literal(1)).Then(literal(2)).Else(literal(3)).End
    assert to_str(expr) == "CASE WHEN 1 THEN 2 ELSE 3 END"


def test_case_with_base_expr_end() -> None:
    base = literal("a")
    expr = Case(base).When(literal(1)).Then(literal(2)).End
    assert to_str(expr) == 'CASE "a" WHEN 1 THEN 2 END'


def test_case_with_base_expr_and_else_end() -> None:
    base = literal("a")
    expr = Case(base).When(literal(1)).Then(literal(2)).Else(literal(3)).End
    assert to_str(expr) == 'CASE "a" WHEN 1 THEN 2 ELSE 3 END'


def test_multiple_when_end() -> None:
    expr = Case.When(literal(1)).Then(literal(2)).When(literal(3)).Then(literal(4)).End
    assert to_str(expr) == "CASE WHEN 1 THEN 2 WHEN 3 THEN 4 END"


def test_multiple_when_with_else_end() -> None:
    expr = (
        Case.When(literal(1))
        .Then(literal(2))
        .When(literal(3))
        .Then(literal(4))
        .Else(literal(5))
        .End
    )
    assert to_str(expr) == "CASE WHEN 1 THEN 2 WHEN 3 THEN 4 ELSE 5 END"


def test_partial_representation() -> None:
    assert to_str(Case(literal(1))) == "CASE 1"
    assert to_str(Case.When(literal(1))) == "CASE WHEN 1"
    assert to_str(Case.When(literal(1)).Then(literal(2))) == "CASE WHEN 1 THEN 2"
    assert (
        to_str(Case.When(literal(1)).Then(literal(2)).Else(literal(3)))
        == "CASE WHEN 1 THEN 2 ELSE 3"
    )


# Note: Calling .End without at least one .When clause is now a compile-time
# error, so a runtime test is no longer needed.
# e.g. `Case(literal(1)).End` will be caught by a static type checker.
