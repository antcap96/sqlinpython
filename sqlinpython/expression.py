from __future__ import annotations

from itertools import repeat
from typing import TYPE_CHECKING, Literal, NoReturn, Type, TypeVar, overload

from sqlinpython.base import SqlElement
from sqlinpython.name import Name
from sqlinpython.select_expression import SelectExpression, SelectExpressionWithAlias

if TYPE_CHECKING:
    import sqlinpython.select  # avoid circular import when importing functions


class Order(SqlElement):
    pass


class OrderWtihNulls(Order):
    def __init__(self, prev: SqlElement, order: bool) -> None:
        self._prev = prev
        self._order = order

    def _create_query(self) -> str:
        if self._order:
            order = "FIRST"
        else:
            order = "LAST"
        return f"{self._prev._create_query()} NULLS {order}"


class OrderWithAscDesc(OrderWtihNulls):
    def __init__(self, prev: SqlElement, ascending: bool) -> None:
        self._prev = prev
        self._ascending = ascending

    def _create_query(self) -> str:
        if self._ascending:
            order = "ASC"
        else:
            order = "DESC"
        return f"{self._prev._create_query()} {order}"

    @property
    def NullsFirst(self) -> OrderWtihNulls:
        return OrderWtihNulls(self, True)

    @property
    def NullsLast(self) -> OrderWtihNulls:
        return OrderWtihNulls(self, False)


class Expression(OrderWithAscDesc, SelectExpression):
    def __init__(self, prev: Expression, other: AndCondition) -> None:
        self._prev = prev
        self._other = other

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} OR {self._other._create_query()}"

    def __bool__(self) -> NoReturn:
        raise ValueError(
            "Expressions don't have truthiness to avoid chained comparisons"
            " behaving unexpectedly"
        )

    def Or(self, other: Expression) -> Expression:
        self_ = _parenthesize_if_necessary(self, Expression)
        other_ = _parenthesize_if_necessary(other, AndCondition)
        return Expression(self_, other_)

    def And(self, other: Expression) -> AndCondition:
        self_ = _parenthesize_if_necessary(self, AndCondition)
        other_ = _parenthesize_if_necessary(other, BooleanCondition)
        return AndCondition(self_, other_)

    def __invert__(self) -> Expression:
        self_ = _parenthesize_if_necessary(self, Condition)
        return BooleanCondition(self_)

    def Like(self, other: Expression) -> Condition:
        self_ = _parenthesize_if_necessary(self, Operand)
        other_ = _parenthesize_if_necessary(other, Operand)
        return OperandWithLike(self_, other_, True)

    def ILike(self, other: Expression) -> Condition:
        self_ = _parenthesize_if_necessary(self, Operand)
        other_ = _parenthesize_if_necessary(other, Operand)
        return OperandWithLike(self_, other_, False)

    def IsNull(self) -> Condition:
        self_ = _parenthesize_if_necessary(self, Operand)
        return OperandIsNull(self_, False)

    def IsNotNull(self) -> Condition:
        self_ = _parenthesize_if_necessary(self, Operand)
        return OperandIsNull(self_, True)

    @overload
    def In(self, other: sqlinpython.select.SelectType, /) -> Condition:
        ...

    @overload
    def In(self, first_other: Expression, /, *others: Expression) -> Condition:
        ...

    def In(
        self,
        first_arg: sqlinpython.select.SelectType | Expression,
        /,
        *other_args: Expression,
    ) -> Condition:
        assert isinstance(first_arg, Expression) or not other_args

        if isinstance(first_arg, Expression):
            self_ = _parenthesize_if_necessary(self, Operand)
            operands = (first_arg, *other_args)
            # At least as of mypy version 0.942, lambda here is necessary
            # for corrent type inference
            operands_ = map(
                lambda x, y: _parenthesize_if_necessary(x, y), operands, repeat(Operand)
            )
            return OperandInOperands(self_, *operands_)
        else:
            self_ = _parenthesize_if_necessary(self, Operand)
            return OperandInSelect(self_, first_arg, False)

    @overload
    def NotIn(self, other: sqlinpython.select.SelectType, /) -> Condition:
        ...

    @overload
    def NotIn(self, first_other: Expression, /, *others: Expression) -> Condition:
        ...

    def NotIn(
        self,
        first_arg: sqlinpython.select.SelectType | Expression,
        /,
        *other_args: Expression,
    ) -> Condition:
        assert isinstance(first_arg, Expression) or not other_args

        if isinstance(first_arg, Expression):
            self_ = _parenthesize_if_necessary(self, Operand)
            operands = (first_arg, *other_args)
            # At least as of mypy version 0.942, lambda here is necessary
            # for corrent type inference
            operands_ = map(
                lambda x, y: _parenthesize_if_necessary(x, y), operands, repeat(Operand)
            )
            return OperandNotInOperands(self_, *operands_)
        else:
            self_ = _parenthesize_if_necessary(self, Operand)
            return OperandInSelect(self_, first_arg, True)

    def Exists(self, other: sqlinpython.select.SelectType) -> Condition:
        self_ = _parenthesize_if_necessary(self, Operand)
        return OperandExists(self_, other, False)

    def NotExists(self, other: sqlinpython.select.SelectType) -> Condition:
        self_ = _parenthesize_if_necessary(self, Operand)
        return OperandExists(self_, other, True)

    def Between(self, low: Expression, high: Expression) -> Condition:
        self_ = _parenthesize_if_necessary(self, Operand)
        low_ = _parenthesize_if_necessary(low, Operand)
        high_ = _parenthesize_if_necessary(high, Operand)
        return OperandBetween(self_, low_, high_, False)

    def NotBetween(self, low: Expression, high: Expression) -> Condition:
        self_ = _parenthesize_if_necessary(self, Operand)
        low_ = _parenthesize_if_necessary(low, Operand)
        high_ = _parenthesize_if_necessary(high, Operand)
        return OperandBetween(self_, low_, high_, True)

    def __lt__(self, other: Expression) -> Condition:
        self_ = _parenthesize_if_necessary(self, Operand)
        other_ = _parenthesize_if_necessary(other, RHSOperand)
        return OperandWithComparison(self_, other_, "<")

    def __le__(self, other: Expression) -> Condition:
        self_ = _parenthesize_if_necessary(self, Operand)
        other_ = _parenthesize_if_necessary(other, RHSOperand)
        return OperandWithComparison(self_, other_, "<=")

    def __gt__(self, other: Expression) -> Condition:
        self_ = _parenthesize_if_necessary(self, Operand)
        other_ = _parenthesize_if_necessary(other, RHSOperand)
        return OperandWithComparison(self_, other_, ">")

    def __ge__(self, other: Expression) -> Condition:
        self_ = _parenthesize_if_necessary(self, Operand)
        other_ = _parenthesize_if_necessary(other, RHSOperand)
        return OperandWithComparison(self_, other_, ">=")

    def __ne__(self, other: Expression) -> Condition:  # type: ignore
        self_ = _parenthesize_if_necessary(self, Operand)
        other_ = _parenthesize_if_necessary(other, RHSOperand)
        return OperandWithComparison(self_, other_, "<>")

    def __eq__(self, other: Expression) -> Condition:  # type: ignore
        self_ = _parenthesize_if_necessary(self, Operand)
        other_ = _parenthesize_if_necessary(other, RHSOperand)
        return OperandWithComparison(self_, other_, "=")

    def __mul__(self, other: Expression) -> Factor:
        self_ = _parenthesize_if_necessary(self, Factor)
        other_ = _parenthesize_if_necessary(other, Term)
        return Factor(self_, other_, "*")

    def __truediv__(self, other: Expression) -> Factor:
        self_ = _parenthesize_if_necessary(self, Factor)
        other_ = _parenthesize_if_necessary(other, Term)
        return Factor(self_, other_, "/")

    def __mod__(self, other: Expression) -> Factor:
        self_ = _parenthesize_if_necessary(self, Factor)
        other_ = _parenthesize_if_necessary(other, Term)
        return Factor(self_, other_, "%")

    def __add__(self, other: Expression) -> Summand:
        self_ = _parenthesize_if_necessary(self, Summand)
        other_ = _parenthesize_if_necessary(other, Factor)
        return Summand(self_, other_, "+")

    def __sub__(self, other: Expression) -> Summand:
        self_ = _parenthesize_if_necessary(self, Summand)
        other_ = _parenthesize_if_necessary(other, Factor)
        return Summand(self_, other_, "-")

    def strcat(self, other: Expression) -> Operand:
        self_ = _parenthesize_if_necessary(self, Operand)
        other_ = _parenthesize_if_necessary(other, Summand)
        return Operand(self_, other_, "||")

    # Order
    @property
    def Asc(self) -> OrderWithAscDesc:
        return OrderWithAscDesc(self, True)

    @property
    def Desc(self) -> OrderWithAscDesc:
        return OrderWithAscDesc(self, False)

    # SelectExpression
    def As(
        self, alias: Name | str, explicit_as: bool = True
    ) -> SelectExpressionWithAlias:
        if isinstance(alias, str):
            alias = Name(alias)

        return SelectExpressionWithAlias(self, alias, explicit_as)


class AndCondition(Expression):
    def __init__(self, prev: AndCondition, other: BooleanCondition) -> None:
        self._prev = prev
        self._other = other

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} AND {self._other._create_query()}"


class BooleanCondition(AndCondition):
    def __init__(self, prev: Condition) -> None:
        self._prev = prev

    def _create_query(self) -> str:
        return f"NOT {self._prev._create_query()}"


class Condition(BooleanCondition):
    pass


class OperandWithComparison(Condition):
    def __init__(
        self,
        prev: Operand,
        other: RHSOperand,
        operation: Literal["=", "<", ">", "<=", ">=", "<>"],
    ):
        self._prev = prev
        self._other = other
        self._operation = operation

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._operation} {self._other._create_query()}"


class OperandWithLike(Condition):
    def __init__(self, prev: Operand, other: Operand, case_sensitive: bool) -> None:
        self._prev = prev
        self._other = other
        self._case_sensitive = case_sensitive

    def _create_query(self) -> str:
        op = "LIKE"
        if not self._case_sensitive:
            op = "ILIKE"
        return f"{self._prev._create_query()} {op} {self._other._create_query()}"


class OperandIsNull(Condition):
    def __init__(self, prev: Operand, negated: bool) -> None:
        self._prev = prev
        self._negated = negated

    def _create_query(self) -> str:
        op = "IS NULL"
        if self._negated:
            op = "IS NOT NULL"
        return f"{self._prev._create_query()} {op}"


class OperandInSelect(Condition):
    def __init__(
        self, prev: Operand, in_select: sqlinpython.select.SelectType, negated: bool
    ) -> None:
        self._prev = prev
        self._in_select = in_select
        self._negated = negated

    def _create_query(self) -> str:
        op = "IN"
        if self._negated:
            op = "NOT IN"
        return f"{self._prev._create_query()} {op} ({self._in_select._create_query()})"


class OperandInOperands(Condition):
    def __init__(self, prev: Operand, *operands: Operand) -> None:
        self._prev = prev
        self._operands = operands

    def _create_query(self) -> str:
        _in = ", ".join(operand._create_query() for operand in self._operands)
        return f"{self._prev._create_query()} IN ({_in})"


class OperandNotInOperands(Condition):
    def __init__(self, prev: Operand, *operands: Operand) -> None:
        self._prev = prev
        self._operands = operands

    def _create_query(self) -> str:
        _in = ", ".join(operand._create_query() for operand in self._operands)
        return f"{self._prev._create_query()} NOT IN ({_in})"


class OperandExists(Condition):
    def __init__(
        self, prev: Operand, other: sqlinpython.select.SelectType, negated: bool
    ) -> None:
        self._prev = prev
        self._other = other  # type: ignore
        self._negated = negated

    def _create_query(self) -> str:
        op = "EXISTS"
        if self._negated:
            op = "NOT EXISTS"
        return f"{self._prev._create_query()} {op} ({self._other._create_query()})"


class OperandBetween(Condition):
    def __init__(
        self, prev: Operand, low: Operand, high: Operand, negated: bool
    ) -> None:
        self._prev = prev
        self._low = low
        self._high = high
        self._negated = negated

    def _create_query(self) -> str:
        op = "BETWEEN"
        if self._negated:
            op = "NOT BETWEEN"
        op += f" {self._low._create_query()} AND {self._high._create_query()}"

        return f"{self._prev._create_query()} {op}"


class RHSOperand(Condition):
    def _create_query(self) -> str:
        return NotImplemented


class AnyOrAllOperand(RHSOperand):
    def __init__(
        self, prev: SqlElement, other: Operand | sqlinpython.select.SelectType
    ):
        self._prev = prev
        self._other = other  # type: ignore

    def _create_query(self) -> str:
        return f"{self._prev._create_query()}({self._other._create_query()})"


class AnyOrAllCall(SqlElement):
    def __call__(
        self, other: Operand | sqlinpython.select.SelectType
    ) -> AnyOrAllOperand:
        return AnyOrAllOperand(self, other)


class AnyKeyword(AnyOrAllCall):
    def _create_query(self) -> str:
        return "ANY"


class AllKeyword(AnyOrAllCall):
    def _create_query(self) -> str:
        return "ALL"


Any = AnyKeyword()
All = AllKeyword()


class Operand(RHSOperand):
    def __init__(self, prev: Operand, other: Summand, operation: Literal["||"]) -> None:
        self._prev = prev
        self._other = other
        self._operation = operation

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._operation} {self._other._create_query()}"


class Summand(Operand):
    def __init__(
        self, prev: Summand, other: Factor, operation: Literal["+", "-"]
    ) -> None:
        self._prev = prev
        self._other = other
        self._operation = operation  # type: ignore

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._operation} {self._other._create_query()}"


class Factor(Summand):
    def __init__(
        self,
        prev: Factor,
        other: Term,
        operation: Literal["*", "/", "%"],
    ) -> None:
        self._prev = prev
        self._other = other
        self._operation = operation  # type: ignore

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._operation} {self._other._create_query()}"


class Term(Factor):
    def __init__(self, prev: TermBeforeBraquets, expression: Expression) -> None:
        self._prev = prev
        self._expression = expression

    def _create_query(self) -> str:
        return f"{self._prev._create_query()}[{self._expression._create_query()}]"


class TermBeforeBraquets(Term):
    def __getitem__(self, expression: Expression) -> Term:
        return Term(self, expression)


class ParenthesizedExpression(TermBeforeBraquets):
    def __init__(self, prev: Expression) -> None:
        self._prev = prev

    def _create_query(self) -> str:
        return f"({self._prev._create_query()})"


class Value(TermBeforeBraquets):
    def __init__(self, value: str | int | float | bool | None, /) -> None:
        self._value = value

    def _create_query(self) -> str:
        if self._value is None:
            return "null"
        elif isinstance(self._value, str):
            return f"'{self._value}'"
        else:
            return str(self._value)


T = TypeVar("T", bound=Expression)


def _parenthesize_if_necessary(
    expression: Expression,
    output_class: Type[T],
) -> T | ParenthesizedExpression:
    if not isinstance(expression, output_class):
        return ParenthesizedExpression(expression)
    else:
        return expression
