from __future__ import annotations

import typing
from itertools import repeat
from os import preadv
from typing import Literal, NoReturn, Sequence, Tuple, Type, TypeVar, overload

from sqlinpython.base import NotImplementedSqlElement, SqlElement


class Select(NotImplementedSqlElement):
    pass


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


class Expression(OrderWithAscDesc):
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
        output = _parenthesize_as_necessary(
            [(self, Expression), (other, AndCondition)], output_class=Expression
        )
        return output

    def And(self, other: Expression) -> AndCondition:
        output = _parenthesize_as_necessary(
            [(self, AndCondition), (other, BooleanCondition)],
            output_class=AndCondition,
        )
        return output

    def __invert__(self) -> Expression:
        output = _parenthesize_as_necessary(
            [(self, Condition)], output_class=BooleanCondition
        )
        return output

    def Like(self, other: Expression) -> Condition:
        output = _parenthesize_as_necessary(
            [(self, Operand), (other, Operand), (True, bool)], output_class=OperandLike
        )
        return output

    def ILike(self, other: Expression) -> Condition:
        output = _parenthesize_as_necessary(
            [(self, Operand), (other, Operand), (False, bool)], output_class=OperandLike
        )
        return output

    def IsNull(self) -> Condition:
        output = _parenthesize_as_necessary(
            [(self, Operand), (False, bool)], output_class=OperandIsNull
        )
        return output

    def IsNotNull(self) -> Condition:
        output = _parenthesize_as_necessary(
            [(self, Operand), (True, bool)], output_class=OperandIsNull
        )
        return output

    @overload
    def In(self, other: Select, /) -> Condition:
        ...

    @overload
    def In(self, first_other: Expression, /, *others: Expression) -> Condition:
        ...

    def In(
        self, first_arg: Select | Expression, /, *other_args: Expression
    ) -> Condition:
        assert not isinstance(first_arg, Select) or not other_args

        if isinstance(first_arg, Select):
            output = _parenthesize_as_necessary(
                [(self, Operand), (first_arg, Select), (False, bool)],
                output_class=OperandInSelect,
            )
            return output
        else:
            operands = (first_arg, *other_args)
            return _parenthesize_as_necessary(
                [(self, Operand), *zip(operands, repeat(Operand))],
                output_class=OperandInOperands,
            )

    @overload
    def NotIn(self, other: Select, /) -> Condition:
        ...

    @overload
    def NotIn(self, first_other: Expression, /, *others: Expression) -> Condition:
        ...

    def NotIn(
        self, first_arg: Select | Expression, /, *other_args: Expression
    ) -> Condition:
        assert not other_args or isinstance(first_arg, Select)

        if isinstance(first_arg, Select):
            output = _parenthesize_as_necessary(
                [(self, Operand), (first_arg, Select), (True, bool)],
                output_class=OperandInSelect,
            )
            return output
        else:
            operands = (first_arg, *other_args)
            return _parenthesize_as_necessary(
                [(self, Operand), *zip(operands, repeat(Operand))],
                output_class=OperandNotInOperands,
            )

    def Exists(self, other: Select) -> Condition:
        return _parenthesize_as_necessary(
            [(self, Operand), (other, Select), (False, bool)],
            output_class=OperandExists,
        )

    def NotExists(self, other: Select) -> Condition:
        return _parenthesize_as_necessary(
            [(self, Operand), (other, Select), (True, bool)], output_class=OperandExists
        )

    def Between(self, low: Expression, high: Expression) -> Condition:
        return _parenthesize_as_necessary(
            [(self, Operand), (low, Operand), (high, Operand), (False, bool)],
            output_class=OperandBetween,
        )

    def NotBetween(self, low: Expression, high: Expression) -> Condition:
        return _parenthesize_as_necessary(
            [(self, Operand), (low, Operand), (high, Operand), (True, bool)],
            output_class=OperandBetween,
        )

    def __lt__(self, other: Expression) -> Condition:
        output = _parenthesize_as_necessary(
            [(self, Operand), (other, RHSOperand)],
            output_class=OperandWithComparison,
            operation="<",
        )
        return output

    def __le__(self, other: Expression) -> Condition:
        output = _parenthesize_as_necessary(
            [(self, Operand), (other, RHSOperand)],
            output_class=OperandWithComparison,
            operation="<=",
        )
        return output

    def __gt__(self, other: Expression) -> Condition:
        output = _parenthesize_as_necessary(
            [(self, Operand), (other, RHSOperand)],
            output_class=OperandWithComparison,
            operation=">",
        )
        return output

    def __ge__(self, other: Expression) -> Condition:
        output = _parenthesize_as_necessary(
            [(self, Operand), (other, RHSOperand)],
            output_class=OperandWithComparison,
            operation=">=",
        )
        return output

    def __ne__(self, other: Expression) -> Condition:  # type: ignore
        output = _parenthesize_as_necessary(
            [(self, Operand), (other, RHSOperand)],
            output_class=OperandWithComparison,
            operation="<>",
        )
        return output

    def __eq__(self, other: Expression) -> Condition:  # type: ignore
        output = _parenthesize_as_necessary(
            [(self, Operand), (other, RHSOperand)],
            output_class=OperandWithComparison,
            operation="=",
        )
        return output

    def __mul__(self, other: Expression) -> Factor:
        return _parenthesize_as_necessary(
            [(self, Factor), (other, Term)], output_class=Factor, operation="*"
        )

    def __truediv__(self, other: Expression) -> Factor:
        return _parenthesize_as_necessary(
            [(self, Factor), (other, Term)], output_class=Factor, operation="/"
        )

    def __mod__(self, other: Expression) -> Factor:
        return _parenthesize_as_necessary(
            [(self, Factor), (other, Term)], output_class=Factor, operation="%"
        )

    def __add__(self, other: Expression) -> Summand:
        return _parenthesize_as_necessary(
            [(self, Summand), (other, Factor)], output_class=Summand, operation="+"
        )

    def __sub__(self, other: Expression) -> Summand:
        return _parenthesize_as_necessary(
            [(self, Summand), (other, Factor)], output_class=Summand, operation="-"
        )

    def strcat(self, other: Expression) -> Operand:
        return _parenthesize_as_necessary(
            [(self, Operand), (other, Summand)], output_class=Operand, operation="||"
        )

    # Order
    @property
    def Asc(self) -> OrderWithAscDesc:
        return OrderWithAscDesc(self, True)

    @property
    def Desc(self) -> OrderWithAscDesc:
        return OrderWithAscDesc(self, False)


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


class OperandLike(Condition):
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
    def __init__(self, prev: Operand, in_select: Select, negated: bool) -> None:
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
    def __init__(self, prev: Operand, other: Select, negated: bool) -> None:
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
    def __init__(self, prev: SqlElement, other: Operand | Select):
        self._prev = prev
        self._other = other  # type: ignore

    def _create_query(self) -> str:
        return f"{self._prev._create_query()}({self._other._create_query()})"


class AnyOrAllCall(SqlElement):
    def __call__(self, other: Operand | Select) -> AnyOrAllOperand:
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


def _parenthesize_as_necessary(
    bound_types: Sequence[Tuple[object, Type[object]]],
    output_class: Type[T],
    **kwargs: typing.Any,
) -> T:
    def parenthesize_if_not_subclass(tup: Tuple[object, Type[object]]) -> typing.Any:
        exp, class_ = tup
        if isinstance(exp, Expression) and not isinstance(exp, class_):
            return ParenthesizedExpression(exp)
        else:
            return exp

    expressions_parenthesized = map(parenthesize_if_not_subclass, bound_types)

    return output_class(*expressions_parenthesized, **kwargs)
