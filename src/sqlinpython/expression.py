from __future__ import annotations

import typing
from typing import overload

from sqlinpython.base import NotImplementedSqlElement, SqlElement
from sqlinpython.indexed_column import IndexedColumnWithCollate
from sqlinpython.name import Name


class SelectStatement(NotImplementedSqlElement):
    pass


class TableFunction(NotImplementedSqlElement):
    pass


# SPEC: https://sqlite.org/lang_expr.html
class Expression(IndexedColumnWithCollate):
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

    def Between(self, lower: Expression, upper: Expression) -> BetweenExpression:
        self_ = _parenthesize_if_necessary(self, Expression4)
        lower_ = _parenthesize_if_necessary(lower, Expression5)
        upper_ = _parenthesize_if_necessary(upper, Expression5)
        return BetweenExpression(self_, lower_, upper_)

    @overload
    def In(self) -> EmptyInExpression: ...
    @overload
    def In(self, select_stmt: SelectStatement, /) -> InExpressionWithSelect: ...
    @overload
    def In(
        self, expr: Expression, /, *exprs: Expression
    ) -> InExpressionWithExpressions: ...
    @overload
    def In(self, table_name: Name, /) -> InExpressionWithTableName: ...
    @overload
    def In(
        self, schema_name: Name, table_name: Name, /
    ) -> InExpressionWithTableName: ...
    @overload
    def In(self, table_function: TableFunction, /) -> InExpressionWithTableFunction: ...
    @overload
    def In(
        self, schema_name: Name, table_function: TableFunction, /
    ) -> InExpressionWithTableFunction: ...
    def In(
        self, *exprs: Expression | SelectStatement | Name | TableFunction
    ) -> (
        EmptyInExpression
        | InExpressionWithSelect
        | InExpressionWithExpressions
        | InExpressionWithTableName
        | InExpressionWithTableFunction
    ):
        self_ = _parenthesize_if_necessary(self, Expression4)
        match exprs:
            case []:
                return EmptyInExpression(self_)
            case [select_stmt] if isinstance(select_stmt, SelectStatement):
                return InExpressionWithSelect(self_, select_stmt)
            case [table_name] if isinstance(table_name, Name):
                return InExpressionWithTableName(self_, table_name)
            case [schema_name, table_name] if isinstance(
                schema_name, Name
            ) and isinstance(table_name, Name):
                return InExpressionWithTableName(self_, schema_name, table_name)
            case [table_function] if isinstance(table_function, TableFunction):
                return InExpressionWithTableFunction(self_, table_function)
            case [schema_name, table_function] if isinstance(
                schema_name, Name
            ) and isinstance(table_function, TableFunction):
                return InExpressionWithTableFunction(self_, schema_name, table_function)
            case _:
                assert all(isinstance(expr, Expression) for expr in exprs)
                exprs = typing.cast(tuple[Expression, ...], exprs)
                return InExpressionWithExpressions(self_, exprs)

    def Glob(self, pattern: Expression) -> MatchLikeExpression:
        self_ = _parenthesize_if_necessary(self, Expression4)
        pattern_ = _parenthesize_if_necessary(pattern, Expression5)
        return MatchLikeExpression(self_, pattern_, "GLOB")

    def Regexp(self, pattern: Expression) -> MatchLikeExpression:
        self_ = _parenthesize_if_necessary(self, Expression4)
        pattern_ = _parenthesize_if_necessary(pattern, Expression5)
        return MatchLikeExpression(self_, pattern_, "REGEXP")

    def Match(self, pattern: Expression) -> MatchLikeExpression:
        self_ = _parenthesize_if_necessary(self, Expression4)
        pattern_ = _parenthesize_if_necessary(pattern, Expression5)
        return MatchLikeExpression(self_, pattern_, "MATCH")

    def Like(self, pattern: Expression) -> LikeExpression:
        self_ = _parenthesize_if_necessary(self, Expression4)
        pattern_ = _parenthesize_if_necessary(pattern, Expression5)
        return LikeExpression(self_, pattern_)

    @property
    def IsNull(self) -> NullCompareExpression:
        self_ = _parenthesize_if_necessary(self, Expression4)
        return NullCompareExpression(self_, "ISNULL")

    @property
    def NotNull(self) -> NullCompareExpression:
        self_ = _parenthesize_if_necessary(self, Expression4)
        return NullCompareExpression(self_, "NOTNULL")

    @property
    def Not(self) -> NegatedOperator:
        self_ = _parenthesize_if_necessary(self, Expression4)
        return NegatedOperator(self_)

    def __lt__(self, other: Expression) -> Comparison:
        self_ = _parenthesize_if_necessary(self, Expression5)
        other_ = _parenthesize_if_necessary(other, Expression6)
        return Comparison(self_, other_, "<")

    def __le__(self, other: Expression) -> Comparison:
        self_ = _parenthesize_if_necessary(self, Expression5)
        other_ = _parenthesize_if_necessary(other, Expression6)
        return Comparison(self_, other_, "<=")

    def __gt__(self, other: Expression) -> Comparison:
        self_ = _parenthesize_if_necessary(self, Expression5)
        other_ = _parenthesize_if_necessary(other, Expression6)
        return Comparison(self_, other_, ">")

    def __ge__(self, other: Expression) -> Comparison:
        self_ = _parenthesize_if_necessary(self, Expression5)
        other_ = _parenthesize_if_necessary(other, Expression6)
        return Comparison(self_, other_, ">=")

    def __and__(self, other: Expression) -> BitOperation:
        self_ = _parenthesize_if_necessary(self, Expression7)
        other_ = _parenthesize_if_necessary(other, Expression8)
        return BitOperation(self_, other_, "&")

    def __or__(self, other: Expression) -> BitOperation:
        self_ = _parenthesize_if_necessary(self, Expression7)
        other_ = _parenthesize_if_necessary(other, Expression8)
        return BitOperation(self_, other_, "|")

    def __lshift__(self, other: Expression) -> BitOperation:
        self_ = _parenthesize_if_necessary(self, Expression7)
        other_ = _parenthesize_if_necessary(other, Expression8)
        return BitOperation(self_, other_, "<<")

    def __rshift__(self, other: Expression) -> BitOperation:
        self_ = _parenthesize_if_necessary(self, Expression7)
        other_ = _parenthesize_if_necessary(other, Expression8)
        return BitOperation(self_, other_, ">>")

    def __add__(self, other: Expression) -> Summand:
        self_ = _parenthesize_if_necessary(self, Expression8)
        other_ = _parenthesize_if_necessary(other, Expression9)
        return Summand(self_, other_, "+")

    def __sub__(self, other: Expression) -> Summand:
        self_ = _parenthesize_if_necessary(self, Expression8)
        other_ = _parenthesize_if_necessary(other, Expression9)
        return Summand(self_, other_, "-")

    def __mul__(self, other: Expression) -> Factor:
        self_ = _parenthesize_if_necessary(self, Expression9)
        other_ = _parenthesize_if_necessary(other, Expression10)
        return Factor(self_, other_, "*")

    def __truediv__(self, other: Expression) -> Factor:
        self_ = _parenthesize_if_necessary(self, Expression9)
        other_ = _parenthesize_if_necessary(other, Expression10)
        return Factor(self_, other_, "/")

    def __mod__(self, other: Expression) -> Factor:
        self_ = _parenthesize_if_necessary(self, Expression9)
        other_ = _parenthesize_if_necessary(other, Expression10)
        return Factor(self_, other_, "%")

    def Concat(self, other: Expression) -> ConcatLikeOperator:
        self_ = _parenthesize_if_necessary(self, Expression10)
        other_ = _parenthesize_if_necessary(other, Expression11)
        return ConcatLikeOperator(self_, other_, "||")

    def Extract(self, other: Expression) -> ConcatLikeOperator:
        self_ = _parenthesize_if_necessary(self, Expression10)
        other_ = _parenthesize_if_necessary(other, Expression11)
        return ConcatLikeOperator(self_, other_, "->")

    def Extract2(self, other: Expression) -> ConcatLikeOperator:
        self_ = _parenthesize_if_necessary(self, Expression10)
        other_ = _parenthesize_if_necessary(other, Expression11)
        return ConcatLikeOperator(self_, other_, "->>")

    def Collate(self, other: Name | str) -> CollateOperator:
        self_ = _parenthesize_if_necessary(self, Expression11)
        if isinstance(other, str):
            other = Name(other)
        return CollateOperator(self_, other)

    def __neg__(self) -> UnaryOperator:
        return UnaryOperator(self, "-")

    def __pos__(self) -> UnaryOperator:
        return UnaryOperator(self, "+")

    def __invert__(self) -> UnaryOperator:
        return UnaryOperator(self, "~")


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
    def __init__(self, prev: Expression4) -> None:
        self._prev = prev

    @property
    def Not(self) -> IsNotExpression:
        return IsNotExpression(self)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} IS"


class BetweenExpression(SqlElement):
    def __init__(self, prev: SqlElement, lower: Expression5, upper: Expression) -> None:
        self._prev = prev
        self._lower = lower
        self._upper = upper

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} BETWEEN {self._lower._create_query()} AND {self._upper._create_query()}"


class EmptyInExpression(Expression4):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} IN ()"


class InExpressionWithSelect(Expression4):
    def __init__(self, prev: SqlElement, select_stmt: SelectStatement) -> None:
        self._prev = prev
        self._select_stmt = select_stmt

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} IN ({self._select_stmt._create_query()})"


class InExpressionWithExpressions(Expression4):
    def __init__(self, prev: SqlElement, exprs: tuple[Expression, ...]) -> None:
        self._prev = prev
        self._exprs = exprs

    def _create_query(self) -> str:
        args = ", ".join(expr._create_query() for expr in self._exprs)
        return f"{self._prev._create_query()} IN ({args})"


class InExpressionWithTableName(Expression4):
    def __init__(
        self, prev: SqlElement, name1: Name, name2: Name | None = None
    ) -> None:
        self._prev = prev
        self._name1 = name1
        self._name2 = name2

    def _create_query(self) -> str:
        if self._name2 is None:
            return f"{self._prev._create_query()} IN {self._name1._create_query()}"
        else:
            return f"{self._prev._create_query()} IN {self._name1._create_query()}.{self._name2._create_query()}"


class InExpressionWithTableFunction(SqlElement):
    def __init__(
        self,
        prev: SqlElement,
        name1: TableFunction | Name,
        name2: TableFunction | None = None,
    ) -> None:
        self._prev = prev
        self._name1 = name1
        self._name2 = name2

    def __call__(self, *args: Expression) -> InExpressionWithTableFunctionArgs:
        return InExpressionWithTableFunctionArgs(self, args)

    def _create_query(self) -> str:
        if self._name2 is None:
            return f"{self._prev._create_query()} IN {self._name1._create_query()}"
        else:
            return f"{self._prev._create_query()} IN {self._name1._create_query()}.{self._name2._create_query()}"


class InExpressionWithTableFunctionArgs(Expression4):
    def __init__(self, prev: SqlElement, exprs: tuple[Expression, ...]) -> None:
        self._prev = prev
        self._exprs = exprs

    def _create_query(self) -> str:
        args = ", ".join(expr._create_query() for expr in self._exprs)
        return f"{self._prev._create_query()}({args})"


class MatchLikeExpression(Expression4):
    def __init__(
        self,
        prev: SqlElement,
        pattern: Expression,
        op: typing.Literal["MATCH", "REGEXP", "GLOB"],
    ) -> None:
        self._prev = prev
        self._pattern = pattern
        self._op = op

    def _create_query(self) -> str:
        return (
            f"{self._prev._create_query()} {self._op} {self._pattern._create_query()}"
        )


# TODO: Maybe this should take prev.prev, pattern and escape, which might allow
# some expressions to not be parenthesized.
class LikeExpressionWithEscape(Expression4):
    def __init__(self, prev: SqlElement, escape: Expression) -> None:
        self._prev = prev
        self._escape = escape

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} ESCAPE {self._escape._create_query()}"


class LikeExpression(LikeExpressionWithEscape):
    def __init__(self, prev: SqlElement, pattern: Expression) -> None:
        self._prev = prev
        self._pattern = pattern

    def Escape(self, escape: Expression) -> LikeExpressionWithEscape:
        return LikeExpressionWithEscape(self, escape)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} LIKE {self._pattern._create_query()}"


class NullCompareExpression(Expression4):
    def __init__(
        self, prev: SqlElement, op: typing.Literal["ISNULL", "NOTNULL", "NULL"]
    ) -> None:
        self._prev = prev
        self._op = op

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._op}"


class NegatedOperator(SqlElement):
    def __init__(self, prev: Expression4) -> None:
        self._prev = prev

    def Between(self, lower: Expression, upper: Expression) -> BetweenExpression:
        lower_ = _parenthesize_if_necessary(lower, Expression5)
        upper_ = _parenthesize_if_necessary(upper, Expression5)
        return BetweenExpression(self, lower_, upper_)

    @overload
    def In(self) -> EmptyInExpression: ...
    @overload
    def In(self, select_stmt: SelectStatement, /) -> InExpressionWithSelect: ...
    @overload
    def In(
        self, expr: Expression, /, *exprs: Expression
    ) -> InExpressionWithExpressions: ...
    @overload
    def In(self, table_name: Name, /) -> InExpressionWithTableName: ...
    @overload
    def In(
        self, schema_name: Name, table_name: Name, /
    ) -> InExpressionWithTableName: ...
    @overload
    def In(self, table_function: TableFunction, /) -> InExpressionWithTableFunction: ...
    @overload
    def In(
        self, schema_name: Name, table_function: TableFunction, /
    ) -> InExpressionWithTableFunction: ...
    def In(
        self, *exprs: Expression | SelectStatement | Name | TableFunction
    ) -> (
        EmptyInExpression
        | InExpressionWithSelect
        | InExpressionWithExpressions
        | InExpressionWithTableName
        | InExpressionWithTableFunction
    ):
        match exprs:
            case []:
                return EmptyInExpression(self)
            case [select_stmt] if isinstance(select_stmt, SelectStatement):
                return InExpressionWithSelect(self, select_stmt)
            case [table_name] if isinstance(table_name, Name):
                return InExpressionWithTableName(self, table_name)
            case [schema_name, table_name] if isinstance(
                schema_name, Name
            ) and isinstance(table_name, Name):
                return InExpressionWithTableName(self, schema_name, table_name)
            case [table_function] if isinstance(table_function, TableFunction):
                return InExpressionWithTableFunction(self, table_function)
            case [schema_name, table_function] if isinstance(
                schema_name, Name
            ) and isinstance(table_function, TableFunction):
                return InExpressionWithTableFunction(self, schema_name, table_function)
            case _:
                assert all(isinstance(expr, Expression) for expr in exprs)
                exprs = typing.cast(tuple[Expression, ...], exprs)
                return InExpressionWithExpressions(self, exprs)

    def Glob(self, pattern: Expression) -> MatchLikeExpression:
        pattern_ = _parenthesize_if_necessary(pattern, Expression5)
        return MatchLikeExpression(self, pattern_, "GLOB")

    def Regexp(self, pattern: Expression) -> MatchLikeExpression:
        pattern_ = _parenthesize_if_necessary(pattern, Expression5)
        return MatchLikeExpression(self, pattern_, "REGEXP")

    def Match(self, pattern: Expression) -> MatchLikeExpression:
        pattern_ = _parenthesize_if_necessary(pattern, Expression5)
        return MatchLikeExpression(self, pattern_, "MATCH")

    def Like(self, pattern: Expression) -> LikeExpression:
        pattern_ = _parenthesize_if_necessary(pattern, Expression5)
        return LikeExpression(self, pattern_)

    @property
    def Null(self) -> NullCompareExpression:
        return NullCompareExpression(self, "NULL")

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} NOT"


class Expression5(Expression4):
    pass


class Comparison(Expression5):
    def __init__(
        self,
        left: Expression,
        right: Expression,
        operator: typing.Literal["<", "<=", ">", ">="],
    ):
        self._left = left
        self._right = right
        self._operator = operator

    def _create_query(self) -> str:
        return f"{self._left._create_query()} {self._operator} {self._right._create_query()}"


class Expression6(Expression5):
    pass


class Expression7(Expression6):
    pass


class BitOperation(Expression7):
    def __init__(
        self,
        left: Expression,
        right: Expression,
        operator: typing.Literal["&", "|", "<<", ">>"],
    ):
        self._left = left
        self._right = right
        self._operator = operator

    def _create_query(self) -> str:
        return f"{self._left._create_query()} {self._operator} {self._right._create_query()}"


class Expression8(Expression7):
    pass


class Summand(Expression8):
    def __init__(
        self, left: Expression, right: Expression, operator: typing.Literal["+", "-"]
    ):
        self._left = left
        self._right = right
        self._operator = operator

    def _create_query(self) -> str:
        return f"{self._left._create_query()} {self._operator} {self._right._create_query()}"


class Expression9(Expression8):
    pass


class Factor(Expression9):
    def __init__(
        self,
        left: Expression,
        right: Expression,
        operator: typing.Literal["*", "/", "%"],
    ):
        self._left = left
        self._right = right
        self._operator = operator

    def _create_query(self) -> str:
        return f"{self._left._create_query()} {self._operator} {self._right._create_query()}"


class Expression10(Expression9):
    pass


class ConcatLikeOperator(Expression10):
    def __init__(
        self,
        left: Expression,
        right: Expression,
        operator: typing.Literal["||", "->", "->>"],
    ):
        self._left = left
        self._right = right
        self._operator = operator

    def _create_query(self) -> str:
        return f"{self._left._create_query()} {self._operator} {self._right._create_query()}"


class Expression11(Expression10):
    pass


class CollateOperator(Expression11):
    def __init__(
        self,
        left: Expression,
        right: Name,
    ):
        self._left = left
        self._right = right

    def _create_query(self) -> str:
        return f"{self._left._create_query()} COLLATE {self._right._create_query()}"


class Expression12(Expression11):
    pass


class UnaryOperator(Expression12):
    def __init__(self, left: Expression, op: typing.Literal["+", "-", "~"]):
        self._left = left
        self._op = op

    def _create_query(self) -> str:
        return f"{self._op}{self._left._create_query()}"


class Expression13(Expression12):
    pass


class ParenthesizedExpression(Expression13):
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


# TODOs:
# bind-parameter
# schema.table.column
# function-call
# tuple
# cast
# Exists
# Case
# raise-function


class Literal(Expression13):
    pass


class CurrentTimeKeyword(Literal):
    def __init__(self) -> None:
        pass

    def _create_query(self) -> str:
        return "CURRENT_TIME"


CurrentTime = CurrentTimeKeyword()


class CurrentDateKeyword(Literal):
    def __init__(self) -> None:
        pass

    def _create_query(self) -> str:
        return "CURRENT_DATE"


CurrentDate = CurrentDateKeyword()


class CurrentTimestampKeyword(Literal):
    def __init__(self) -> None:
        pass

    def _create_query(self) -> str:
        return "CURRENT_TIMESTAMP"


CurrentTimestamp = CurrentTimestampKeyword()


class FloatLiteral(Literal):
    def __init__(self, value: float) -> None:
        self._value = value

    # TODO: All this
    def _create_query(self) -> str:
        return str(self._value)


class IntLiteral(Literal):
    def __init__(self, value: int) -> None:
        self._value = value

    def _create_query(self) -> str:
        return str(self._value)


class StringLiteral(Literal):
    def __init__(self, value: str) -> None:
        self._value = value

    def _create_query(self) -> str:
        return f'"{self._value}"'


class BooleanLiteral(Literal):
    def __init__(self, value: bool) -> None:
        self._value = value

    def _create_query(self) -> str:
        return str(self._value).upper()


class NullLiteral(Literal):
    def __init__(self) -> None:
        pass

    def _create_query(self) -> str:
        return "NULL"


type SqlLiteral = float | str | None | bool


def literal(value: SqlLiteral) -> Literal:
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
