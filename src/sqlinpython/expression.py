from __future__ import annotations

from sqlinpython.base import SqlElement


class Expression(SqlElement):
    def Or(self, other: Expression) -> OrCondition:
        self_ = _parenthesize_if_necessary(self, Expression1)
        other_ = _parenthesize_if_necessary(other, Expression2)
        return OrCondition(self_, other_)

    def And(self, other: Expression) -> AndCondition:
        self_ = _parenthesize_if_necessary(self, Expression2)
        other_ = _parenthesize_if_necessary(other, Expression3)
        return AndCondition(self_, other_)

    def eq(self, other: Expression, double_eq: bool = False) -> EqExpression:
        self_ = _parenthesize_if_necessary(self, Expression4)
        other_ = _parenthesize_if_necessary(other, Expression5)
        return EqExpression(self_, other_, double_eq)

    def ne(self, other: Expression, arrows: bool = False) -> NeExpression:
        self_ = _parenthesize_if_necessary(self, Expression4)
        other_ = _parenthesize_if_necessary(other, Expression5)
        return NeExpression(self_, other_, arrows)

    @property
    def Is(self) -> IsExpression:
        self_ = _parenthesize_if_necessary(self, Expression4)
        return IsExpression(self_)


class Expression1(Expression):
    pass


class OrCondition(Expression1):
    def __init__(self, left: Expression1, right: Expression2) -> None:
        self._left = left
        self._right = right

    def _create_query(self) -> str:
        return f"{self._left._create_query()} OR {self._right._create_query()}"


class Expression2(Expression1):
    pass


class AndCondition(Expression2):
    def __init__(self, left: Expression2, right: Expression3) -> None:
        self._left = left
        self._right = right

    def _create_query(self) -> str:
        return f"{self._left._create_query()} AND {self._right._create_query()}"


class Expression3(Expression2):
    pass


class NotKeyword:
    def __call__(self, after: Expression) -> NotExpression:
        _after = _parenthesize_if_necessary(after, Expression3)
        return NotExpression(_after)


Not = NotKeyword()


class NotExpression(Expression3):
    def __init__(self, after: Expression3) -> None:
        self._after = after

    def _create_query(self) -> str:
        return f"NOT {self._after._create_query()}"


class Expression4(Expression3):
    pass


class EqExpression(Expression4):
    def __init__(self, left: Expression4, right: Expression5, double_eq: bool) -> None:
        self._left = left
        self._right = right
        self._double_eq = double_eq

    def _create_query(self) -> str:
        if self._double_eq:
            op = "=="
        else:
            op = "="
        return f"{self._left._create_query()} {op} {self._right._create_query()}"


class NeExpression(Expression4):
    def __init__(self, left: Expression4, right: Expression5, arrows: bool) -> None:
        self._left = left
        self._right = right
        self._arrows = arrows

    def _create_query(self) -> str:
        if self._arrows:
            op = "<>"
        else:
            op = "!="
        return f"{self._left._create_query()} {op} {self._right._create_query()}"


class IsExpressionComplete(Expression4):
    def __init__(self, prev: SqlElement, other: Expression4) -> None:
        self._prev = prev
        self._other = other

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._other._create_query()}"


class IsDistinctFromExpression(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def __call__(self, other: Expression) -> IsExpressionComplete:
        _other = _parenthesize_if_necessary(other, Expression4)
        return IsExpressionComplete(self, _other)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} DISTINCT FROM"


class IsNotExpression(IsDistinctFromExpression):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def DistinctFrom(self) -> IsDistinctFromExpression:
        return IsDistinctFromExpression(self)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} NOT"


class IsExpression(IsNotExpression):
    def __init__(self, prev: Expression3) -> None:
        self._prev = prev

    @property
    def Not(self) -> IsNotExpression:
        return IsNotExpression(self)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} IS"


class Expression5(Expression4):
    pass


class Expression6(Expression5):
    pass


class Expression7(Expression6):
    pass


class Expression8(Expression7):
    pass


class Expression9(Expression8):
    pass


class Expression10(Expression9):
    pass


class Expression11(Expression10):
    pass


class Expression12(Expression11):
    pass


class ParenthesizedExpression(Expression12):
    def __init__(self, prev: Expression) -> None:
        self._prev = prev

    def _create_query(self) -> str:
        return f"({self._prev._create_query()})"


def _parenthesize_if_necessary[T](
    expression: Expression,
    output_class: type[T],
) -> T | ParenthesizedExpression:
    if not isinstance(expression, output_class):
        return ParenthesizedExpression(expression)
    else:
        return expression


class FloatLiteral(Expression12):
    def __init__(self, value: float) -> None:
        self._value = value

    # TODO: All this
    def _create_query(self) -> str:
        return str(self._value)


class IntLiteral(Expression12):
    def __init__(self, value: int) -> None:
        self._value = value

    def _create_query(self) -> str:
        return str(self._value)


class StringLiteral(Expression12):
    def __init__(self, value: str) -> None:
        self._value = value

    def _create_query(self) -> str:
        return f'"{self._value}"'


class BooleanLiteral(Expression12):
    def __init__(self, value: bool) -> None:
        self._value = value

    def _create_query(self) -> str:
        return str(self._value).upper()


class NullLiteral(Expression12):
    def __init__(self) -> None:
        pass

    def _create_query(self) -> str:
        return "NULL"


type SqlLiteral = float | str | None | bool


def Literal(value: SqlLiteral) -> Expression12:
    # The order of bool, int and float is necessary due to the type hierarchy
    if isinstance(value, bool):
        return BooleanLiteral(value)
    elif isinstance(value, int):
        return IntLiteral(value)
    elif isinstance(value, float):
        return FloatLiteral(value)
    elif isinstance(value, str):
        return StringLiteral(value)
    elif value is None:
        return NullLiteral()
    else:
        raise ValueError(f"Unsupported literal type: {type(value)}")
