from __future__ import annotations

import typing
from abc import ABC
from typing import overload, override

from sqlinpython.base import NotImplementedSqlElement, SqlElement, comma_separated
from sqlinpython.expression.frame_bound import IHasFrameBounds
from sqlinpython.indexed_column import IHasAscDesc
from sqlinpython.name import Name
from sqlinpython.savepoint import RollbackKeyword
from sqlinpython.select_base import SelectStatement, SelectStatement_
from sqlinpython.type_name import CompleteTypeName


class TableFunction(NotImplementedSqlElement):
    pass


# SPEC: https://sqlite.org/lang_expr.html
class INegatedOperations(SqlElement, ABC):
    def Between(self, lower: Expression, upper: Expression) -> BetweenExpression:
        if isinstance(self, Expression):
            self_ = self._wrap_parenthesis_if_not(Expression4)
        else:
            self_ = self
        lower_ = lower._wrap_parenthesis_if_not(Expression5)
        upper_ = upper._wrap_parenthesis_if_not(Expression5)
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
        if isinstance(self, Expression):
            self_ = self._wrap_parenthesis_if_not(Expression4)
        else:
            self_ = self
        match exprs:
            case []:
                return EmptyInExpression(self_)
            case [select_stmt] if isinstance(select_stmt, SelectStatement_):
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
        if isinstance(self, Expression):
            self_ = self._wrap_parenthesis_if_not(Expression4)
        else:
            self_ = self
        pattern_ = pattern._wrap_parenthesis_if_not(Expression5)
        return MatchLikeExpression(self_, pattern_, "GLOB")

    def Regexp(self, pattern: Expression) -> MatchLikeExpression:
        if isinstance(self, Expression):
            self_ = self._wrap_parenthesis_if_not(Expression4)
        else:
            self_ = self
        pattern_ = pattern._wrap_parenthesis_if_not(Expression5)
        return MatchLikeExpression(self_, pattern_, "REGEXP")

    def Match(self, pattern: Expression) -> MatchLikeExpression:
        if isinstance(self, Expression):
            self_ = self._wrap_parenthesis_if_not(Expression4)
        else:
            self_ = self
        pattern_ = pattern._wrap_parenthesis_if_not(Expression5)
        return MatchLikeExpression(self_, pattern_, "MATCH")

    def Like(self, pattern: Expression) -> LikeExpression:
        if isinstance(self, Expression):
            self_ = self._wrap_parenthesis_if_not(Expression4)
        else:
            self_ = self
        pattern_ = pattern._wrap_parenthesis_if_not(Expression5)
        return LikeExpression(self_, pattern_)


class Expression(IHasAscDesc, INegatedOperations, IHasFrameBounds, ABC):
    def As(self, alias: str | Name, /) -> AliasedExpression:
        if isinstance(alias, str):
            alias = Name(alias)
        return AliasedExpression(self, alias)

    def Or(self, other: Expression) -> OrCondition:
        self_ = self._wrap_parenthesis_if_not(Expression1)
        other_ = other._wrap_parenthesis_if_not(Expression2)
        return OrCondition(self_, other_)

    def And(self, other: Expression) -> AndCondition:
        self_ = self._wrap_parenthesis_if_not(Expression2)
        other_ = other._wrap_parenthesis_if_not(Expression3)
        return AndCondition(self_, other_)

    def eq(self, other: Expression, double_eq: bool = False) -> EqExpression:
        self_ = self._wrap_parenthesis_if_not(Expression4)
        other_ = other._wrap_parenthesis_if_not(Expression5)
        return EqExpression(self_, other_, double_eq)

    def ne(self, other: Expression, arrows: bool = False) -> NeExpression:
        self_ = self._wrap_parenthesis_if_not(Expression4)
        other_ = other._wrap_parenthesis_if_not(Expression5)
        return NeExpression(self_, other_, arrows)

    @property
    def Is(self) -> IsExpression:
        self_ = self._wrap_parenthesis_if_not(Expression4)
        return IsExpression(self_)

    @property
    def IsNull(self) -> NullCompareExpression:
        self_ = self._wrap_parenthesis_if_not(Expression4)
        return NullCompareExpression(self_, "ISNULL")

    @property
    def Notnull(self) -> NullCompareExpression:
        self_ = self._wrap_parenthesis_if_not(Expression4)
        return NullCompareExpression(self_, "NOTNULL")

    @property
    def Not(self) -> NegatedOperator:
        self_ = self._wrap_parenthesis_if_not(Expression4)
        return NegatedOperator(self_)

    def __lt__(self, other: Expression) -> Comparison:
        self_ = self._wrap_parenthesis_if_not(Expression5)
        other_ = other._wrap_parenthesis_if_not(Expression6)
        return Comparison(self_, other_, "<")

    def __le__(self, other: Expression) -> Comparison:
        self_ = self._wrap_parenthesis_if_not(Expression5)
        other_ = other._wrap_parenthesis_if_not(Expression6)
        return Comparison(self_, other_, "<=")

    def __gt__(self, other: Expression) -> Comparison:
        self_ = self._wrap_parenthesis_if_not(Expression5)
        other_ = other._wrap_parenthesis_if_not(Expression6)
        return Comparison(self_, other_, ">")

    def __ge__(self, other: Expression) -> Comparison:
        self_ = self._wrap_parenthesis_if_not(Expression5)
        other_ = other._wrap_parenthesis_if_not(Expression6)
        return Comparison(self_, other_, ">=")

    def __and__(self, other: Expression) -> BitOperation:
        self_ = self._wrap_parenthesis_if_not(Expression7)
        other_ = other._wrap_parenthesis_if_not(Expression8)
        return BitOperation(self_, other_, "&")

    def __or__(self, other: Expression) -> BitOperation:
        self_ = self._wrap_parenthesis_if_not(Expression7)
        other_ = other._wrap_parenthesis_if_not(Expression8)
        return BitOperation(self_, other_, "|")

    def __lshift__(self, other: Expression) -> BitOperation:
        self_ = self._wrap_parenthesis_if_not(Expression7)
        other_ = other._wrap_parenthesis_if_not(Expression8)
        return BitOperation(self_, other_, "<<")

    def __rshift__(self, other: Expression) -> BitOperation:
        self_ = self._wrap_parenthesis_if_not(Expression7)
        other_ = other._wrap_parenthesis_if_not(Expression8)
        return BitOperation(self_, other_, ">>")

    def __add__(self, other: Expression) -> Summand:
        self_ = self._wrap_parenthesis_if_not(Expression8)
        other_ = other._wrap_parenthesis_if_not(Expression9)
        return Summand(self_, other_, "+")

    def __sub__(self, other: Expression) -> Summand:
        self_ = self._wrap_parenthesis_if_not(Expression8)
        other_ = other._wrap_parenthesis_if_not(Expression9)
        return Summand(self_, other_, "-")

    def __mul__(self, other: Expression) -> Factor:
        self_ = self._wrap_parenthesis_if_not(Expression9)
        other_ = other._wrap_parenthesis_if_not(Expression10)
        return Factor(self_, other_, "*")

    def __truediv__(self, other: Expression) -> Factor:
        self_ = self._wrap_parenthesis_if_not(Expression9)
        other_ = other._wrap_parenthesis_if_not(Expression10)
        return Factor(self_, other_, "/")

    def __mod__(self, other: Expression) -> Factor:
        self_ = self._wrap_parenthesis_if_not(Expression9)
        other_ = other._wrap_parenthesis_if_not(Expression10)
        return Factor(self_, other_, "%")

    def Concat(self, other: Expression) -> ConcatLikeOperator:
        self_ = self._wrap_parenthesis_if_not(Expression10)
        other_ = other._wrap_parenthesis_if_not(Expression11)
        return ConcatLikeOperator(self_, other_, "||")

    def Extract(self, other: Expression) -> ConcatLikeOperator:
        self_ = self._wrap_parenthesis_if_not(Expression10)
        other_ = other._wrap_parenthesis_if_not(Expression11)
        return ConcatLikeOperator(self_, other_, "->")

    def Extract2(self, other: Expression) -> ConcatLikeOperator:
        self_ = self._wrap_parenthesis_if_not(Expression10)
        other_ = other._wrap_parenthesis_if_not(Expression11)
        return ConcatLikeOperator(self_, other_, "->>")

    def Collate(self, other: Name | str, /) -> CollateOperator:
        self_ = self._wrap_parenthesis_if_not(Expression11)
        if isinstance(other, str):
            other = Name(other)
        return CollateOperator(self_, other)

    def __neg__(self) -> UnaryOperator:
        return UnaryOperator(self, "-")

    def __pos__(self) -> UnaryOperator:
        return UnaryOperator(self, "+")

    def __invert__(self) -> UnaryOperator:
        return UnaryOperator(self, "~")

    def _wrap_parenthesis_if_not[T](
        self, output_class: type[T]
    ) -> T | ParenthesizedExpression:
        if not isinstance(self, output_class):
            return ParenthesizedExpression(self)
        else:
            return self


class AliasedExpression(SqlElement):
    def __init__(
        self, expression: Expression, alias: Name, *, explicit_as: bool = True
    ) -> None:
        self._expression = expression
        self._alias = alias
        self._explicit_as = explicit_as

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._expression._create_query(buffer)
        if self._explicit_as:
            buffer.append(" AS ")
        else:
            buffer.append(" ")
        self._alias._create_query(buffer)


class Expression1(Expression, ABC):
    pass


class OrCondition(Expression1):
    def __init__(self, left: Expression1, right: Expression2) -> None:
        self._left = left
        self._right = right

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._left._create_query(buffer)
        buffer.append(" OR ")
        self._right._create_query(buffer)


class Expression2(Expression1, ABC):
    pass


class AndCondition(Expression2):
    def __init__(self, left: Expression2, right: Expression3) -> None:
        self._left = left
        self._right = right

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._left._create_query(buffer)
        buffer.append(" AND ")
        self._right._create_query(buffer)


class Expression3(Expression2, ABC):
    pass


class NotKeyword:
    def __call__(self, after: Expression) -> NotExpression:
        return NotExpression(after._wrap_parenthesis_if_not(Expression3))

    def Exists(self, select_stmt: SelectStatement) -> NotExpression:
        return NotExpression(Exists(select_stmt))


Not = NotKeyword()


class NotExpression(Expression3):
    def __init__(self, after: Expression3) -> None:
        self._after = after

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("NOT ")
        self._after._create_query(buffer)


class Expression4(Expression3, ABC):
    pass


class EqExpression(Expression4):
    def __init__(self, left: Expression4, right: Expression5, double_eq: bool) -> None:
        self._left = left
        self._right = right
        self._double_eq = double_eq

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._left._create_query(buffer)
        if self._double_eq:
            op = " == "
        else:
            op = " = "
        buffer.append(op)
        self._right._create_query(buffer)


class NeExpression(Expression4):
    def __init__(self, left: Expression4, right: Expression5, arrows: bool) -> None:
        self._left = left
        self._right = right
        self._arrows = arrows

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._left._create_query(buffer)
        if self._arrows:
            op = " <> "
        else:
            op = " != "
        buffer.append(op)
        self._right._create_query(buffer)


class IsExpressionComplete(Expression4):
    def __init__(self, prev: IIsCallable, other: Expression4) -> None:
        self._prev = prev
        self._other = other

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._other._create_query(buffer)


class IIsCallable(SqlElement, ABC):
    def __call__(self, other: Expression) -> IsExpressionComplete:
        _other = other._wrap_parenthesis_if_not(Expression4)
        return IsExpressionComplete(self, _other)


class IsDistinctFromExpression(IIsCallable):
    def __init__(self, prev: IIsCallable) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" DISTINCT FROM")


class IsNotExpression(IIsCallable):
    def __init__(self, prev: IsExpression) -> None:
        self._prev = prev

    @property
    def DistinctFrom(self) -> IsDistinctFromExpression:
        return IsDistinctFromExpression(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" NOT")


class IsExpression(IIsCallable):
    def __init__(self, prev: Expression4) -> None:
        self._prev = prev

    @property
    def Not(self) -> IsNotExpression:
        return IsNotExpression(self)

    @property
    def DistinctFrom(self) -> IsDistinctFromExpression:
        return IsDistinctFromExpression(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IS")


class BetweenExpression(SqlElement):
    def __init__(
        self, prev: SqlElement, lower: Expression5, upper: Expression5
    ) -> None:
        self._prev = prev
        self._lower = lower
        self._upper = upper

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" BETWEEN ")
        self._lower._create_query(buffer)
        buffer.append(" AND ")
        self._upper._create_query(buffer)


class EmptyInExpression(Expression4):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IN ()")


class InExpressionWithSelect(Expression4):
    def __init__(self, prev: SqlElement, select_stmt: SelectStatement) -> None:
        self._prev = prev
        self._select_stmt = select_stmt

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IN (")
        self._select_stmt._create_query(buffer)
        buffer.append(")")


class InExpressionWithExpressions(Expression4):
    def __init__(self, prev: SqlElement, exprs: tuple[Expression, ...]) -> None:
        self._prev = prev
        self._exprs = exprs

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IN (")
        comma_separated(buffer, self._exprs)
        buffer.append(")")


class InExpressionWithTableName(Expression4):
    def __init__(
        self, prev: SqlElement, schema: Name, name: Name | None = None
    ) -> None:
        self._prev = prev
        self._schema = schema
        self._name = name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IN ")
        self._schema._create_query(buffer)
        if self._name is not None:
            buffer.append(".")
            self._name._create_query(buffer)


class InExpressionWithTableFunction(SqlElement):
    def __init__(
        self,
        prev: SqlElement,
        schema: TableFunction | Name,
        name: TableFunction | None = None,
    ) -> None:
        self._prev = prev
        self._schema = schema
        self._name = name

    def __call__(self, *args: Expression) -> InExpressionWithTableFunctionArgs:
        return InExpressionWithTableFunctionArgs(self, args)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IN ")
        self._schema._create_query(buffer)
        if self._name is not None:
            buffer.append(".")
            self._name._create_query(buffer)


class InExpressionWithTableFunctionArgs(Expression4):
    def __init__(self, prev: SqlElement, exprs: tuple[Expression, ...]) -> None:
        self._prev = prev
        self._exprs = exprs

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append("(")
        comma_separated(buffer, self._exprs)
        buffer.append(")")


class MatchLikeExpression(Expression4):
    def __init__(
        self,
        prev: SqlElement,
        pattern: Expression5,
        op: typing.Literal["MATCH", "REGEXP", "GLOB"],
    ) -> None:
        self._prev = prev
        self._pattern = pattern
        self._op = op

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._op} ")
        self._pattern._create_query(buffer)


# TODO: Maybe this should take prev.prev, pattern and escape, which might allow
# some expressions to not be parenthesized.
class LikeExpressionWithEscape(Expression4):
    def __init__(self, prev: LikeExpression, escape: Expression) -> None:
        self._prev = prev
        self._escape = escape

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ESCAPE ")
        self._escape._create_query(buffer)


class LikeExpression(Expression4):
    def __init__(self, prev: SqlElement, pattern: Expression5) -> None:
        self._prev = prev
        self._pattern = pattern

    def Escape(self, escape: Expression) -> LikeExpressionWithEscape:
        return LikeExpressionWithEscape(self, escape)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" LIKE ")
        self._pattern._create_query(buffer)


class NullCompareExpression(Expression4):
    def __init__(
        self, prev: SqlElement, op: typing.Literal["ISNULL", "NOTNULL", "NULL"]
    ) -> None:
        self._prev = prev
        self._op = op

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._op}")


class NegatedOperator(INegatedOperations):
    def __init__(self, prev: Expression4) -> None:
        self._prev = prev

    @property
    def Null(self) -> NullCompareExpression:
        return NullCompareExpression(self, "NULL")

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" NOT")


class Expression5(Expression4, ABC):
    pass


class Comparison(Expression5):
    def __init__(
        self,
        left: Expression5,
        right: Expression6,
        operator: typing.Literal["<", "<=", ">", ">="],
    ):
        self._left = left
        self._right = right
        self._operator = operator

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._left._create_query(buffer)
        buffer.append(f" {self._operator} ")
        self._right._create_query(buffer)


class Expression6(Expression5, ABC):
    pass


class Expression7(Expression6, ABC):
    pass


class BitOperation(Expression7):
    def __init__(
        self,
        left: Expression7,
        right: Expression8,
        operator: typing.Literal["&", "|", "<<", ">>"],
    ):
        self._left = left
        self._right = right
        self._operator = operator

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._left._create_query(buffer)
        buffer.append(f" {self._operator} ")
        self._right._create_query(buffer)


class Expression8(Expression7, ABC):
    pass


class Summand(Expression8):
    def __init__(
        self, left: Expression8, right: Expression9, operator: typing.Literal["+", "-"]
    ):
        self._left = left
        self._right = right
        self._operator = operator

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._left._create_query(buffer)
        buffer.append(f" {self._operator} ")
        self._right._create_query(buffer)


class Expression9(Expression8, ABC):
    pass


class Factor(Expression9):
    def __init__(
        self,
        left: Expression9,
        right: Expression10,
        operator: typing.Literal["*", "/", "%"],
    ):
        self._left = left
        self._right = right
        self._operator = operator

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._left._create_query(buffer)
        buffer.append(f" {self._operator} ")
        self._right._create_query(buffer)


class Expression10(Expression9, ABC):
    pass


class ConcatLikeOperator(Expression10):
    def __init__(
        self,
        left: Expression10,
        right: Expression11,
        operator: typing.Literal["||", "->", "->>"],
    ):
        self._left = left
        self._right = right
        self._operator = operator

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._left._create_query(buffer)
        buffer.append(f" {self._operator} ")
        self._right._create_query(buffer)


class Expression11(Expression10, ABC):
    pass


class CollateOperator(Expression11):
    def __init__(
        self,
        left: Expression11,
        right: Name,
    ):
        self._left = left
        self._right = right

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._left._create_query(buffer)
        buffer.append(" COLLATE ")
        self._right._create_query(buffer)


class Expression12(Expression11, ABC):
    pass


class UnaryOperator(Expression12):
    def __init__(self, left: Expression, op: typing.Literal["+", "-", "~"]):
        self._left = left
        self._op = op

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append(self._op)
        self._left._create_query(buffer)


class Expression13(Expression12, ABC):
    pass


class ParenthesizedExpression(Expression13):
    def __init__(self, prev: Expression) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("(")
        self._prev._create_query(buffer)
        buffer.append(")")


class Row(Expression13):
    def __init__(
        self, *exprs: *tuple[Expression, Expression, *tuple[Expression, ...]]
    ) -> None:
        self._exprs = exprs

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("(")
        comma_separated(buffer, self._exprs)
        buffer.append(")")


class Cast(Expression13):
    def __init__(self, expr: Expression, type_name: CompleteTypeName) -> None:
        self._expr = expr
        self._type_name = type_name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("CAST(")
        self._expr._create_query(buffer)
        buffer.append(" AS ")
        self._type_name._create_query(buffer)
        buffer.append(")")


class Subquery(Expression13):
    def __init__(self, select_stmt: SelectStatement) -> None:
        self._select_stmt = select_stmt

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("(")
        self._select_stmt._create_query(buffer)
        buffer.append(")")


class Exists(Expression13):
    def __init__(self, select_stmt: SelectStatement) -> None:
        self._select_stmt = select_stmt

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("EXISTS (")
        self._select_stmt._create_query(buffer)
        buffer.append(")")


class IgnoreKeyword:
    pass


Ignore = IgnoreKeyword()


class AbortKeyword:
    pass


Abort = AbortKeyword()


class FailKeyword:
    pass


Fail = FailKeyword()


class RaiseExpression(Expression13):
    def __init__(
        self,
        mode: typing.Literal["IGNORE", "ROLLBACK", "ABORT", "FAIL"],
        message: str | None,
    ) -> None:
        from .literal import StringLiteral

        self._mode = mode
        self._message = StringLiteral(message) if message is not None else None

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append(f"RAISE({self._mode}")
        if self._message is not None:
            buffer.append(", ")
            self._message._create_query(buffer)
        buffer.append(")")


class RaiseKeyword:
    @property
    def Ignore(self) -> RaiseExpression:
        return RaiseExpression("IGNORE", None)

    def Rollback(self, message: str) -> RaiseExpression:
        return RaiseExpression("ROLLBACK", message)

    def Abort(self, message: str) -> RaiseExpression:
        return RaiseExpression("ABORT", message)

    def Fail(self, message: str) -> RaiseExpression:
        return RaiseExpression("FAIL", message)

    @overload
    def __call__(
        self, mode: typing.Literal["IGNORE"] | IgnoreKeyword, /
    ) -> RaiseExpression: ...
    @overload
    def __call__(
        self,
        mode: typing.Literal["ROLLBACK"] | RollbackKeyword,
        message: str,
        /,
    ) -> RaiseExpression: ...
    @overload
    def __call__(
        self,
        mode: typing.Literal["ABORT"] | AbortKeyword,
        message: str,
        /,
    ) -> RaiseExpression: ...
    @overload
    def __call__(
        self,
        mode: typing.Literal["FAIL"] | FailKeyword,
        message: str,
        /,
    ) -> RaiseExpression: ...
    def __call__(
        self,
        mode: typing.Literal["IGNORE", "ROLLBACK", "ABORT", "FAIL"]
        | IgnoreKeyword
        | RollbackKeyword
        | AbortKeyword
        | FailKeyword,
        message: str | None = None,
        /,
    ) -> RaiseExpression:
        if isinstance(mode, IgnoreKeyword):
            return RaiseExpression("IGNORE", message)
        elif isinstance(mode, RollbackKeyword):
            return RaiseExpression("ROLLBACK", message)
        elif isinstance(mode, AbortKeyword):
            return RaiseExpression("ABORT", message)
        elif isinstance(mode, FailKeyword):
            return RaiseExpression("FAIL", message)
        else:
            return RaiseExpression(mode, message)


Raise = RaiseKeyword()


class TableColumnName(Expression12):
    def __init__(self, table: Name | str, column: Name | str) -> None:
        if isinstance(table, str):
            table = Name(table)
        if isinstance(column, str):
            column = Name(column)
        self._table = table
        self._column = column

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._table._create_query(buffer)
        buffer.append(".")
        self._column._create_query(buffer)


class SchemaTableColumnName(Expression12):
    def __init__(
        self, schema: Name | str, table: Name | str, column: Name | str
    ) -> None:
        if isinstance(schema, str):
            schema = Name(schema)
        if isinstance(table, str):
            table = Name(table)
        if isinstance(column, str):
            column = Name(column)
        self._schema = schema
        self._table = table
        self._column = column

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._schema._create_query(buffer)
        buffer.append(".")
        self._table._create_query(buffer)
        buffer.append(".")
        self._column._create_query(buffer)
