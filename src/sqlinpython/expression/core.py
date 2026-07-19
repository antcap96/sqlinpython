from __future__ import annotations

import typing
from abc import ABC
from typing import TYPE_CHECKING, NoReturn, overload, override

from sqlinpython.base import NoArg, SqlElement, comma_separated
from sqlinpython.expression.frame_bound import IHasFrameBounds
from sqlinpython.indexed_column import IHasAscDesc
from sqlinpython.name import Name
from sqlinpython.select_base import SelectStatement, SelectStatement_
from sqlinpython.type_name import CompleteTypeName

if TYPE_CHECKING:
    from sqlinpython.expression.literal import ExpressionOrLiteral
    from sqlinpython.table_or_subquery import TableFunctionRefCall


def _to_expr(value: ExpressionOrLiteral) -> Expression:
    # Deferred import: literal.py imports Expression from this module.
    from sqlinpython.expression.literal import to_expr

    return to_expr(value)


# SPEC: https://sqlite.org/lang_expr.html
class INegatedOperations(SqlElement, ABC):
    def Between(
        self, lower: ExpressionOrLiteral, upper: ExpressionOrLiteral
    ) -> BetweenExpression:
        if isinstance(self, Expression):
            self_ = self._wrap_parenthesis_if_not(ComparisonPrecedence)
        else:
            self_ = self
        lower_ = _to_expr(lower)._wrap_parenthesis_if_not(RelationalPrecedence)
        upper_ = _to_expr(upper)._wrap_parenthesis_if_not(RelationalPrecedence)
        return BetweenExpression(self_, lower_, upper_)

    @overload
    def In(self) -> EmptyInExpression: ...
    @overload
    def In(self, select_stmt: SelectStatement, /) -> InExpressionWithSelect: ...
    @overload
    def In(
        self, expr: ExpressionOrLiteral, /, *exprs: ExpressionOrLiteral
    ) -> InExpressionWithExpressions: ...
    @overload
    def In(self, table_name: Name, /) -> InExpressionWithTableName: ...
    @overload
    def In(
        self, schema_name: Name, table_name: Name, /
    ) -> InExpressionWithTableName: ...
    @overload
    def In(
        self, table_function: TableFunctionRefCall, /
    ) -> InExpressionWithTableFunction: ...
    def In(
        self,
        *exprs: ExpressionOrLiteral | SelectStatement | Name | TableFunctionRefCall,
    ) -> (
        EmptyInExpression
        | InExpressionWithSelect
        | InExpressionWithExpressions
        | InExpressionWithTableName
        | InExpressionWithTableFunction
    ):
        # Deferred import: table_or_subquery imports from this module.
        from sqlinpython.table_or_subquery import TableFunctionRefCall

        if isinstance(self, Expression):
            self_ = self._wrap_parenthesis_if_not(ComparisonPrecedence)
        else:
            self_ = self
        match exprs:
            case []:
                return EmptyInExpression(self_)
            case [select_stmt] if isinstance(select_stmt, SelectStatement_):
                return InExpressionWithSelect(self_, select_stmt)
            case [table_function] if isinstance(table_function, TableFunctionRefCall):
                return InExpressionWithTableFunction(self_, table_function)
            case [table_name] if isinstance(table_name, Name):
                return InExpressionWithTableName(self_, table_name)
            case [schema_name, table_name] if isinstance(
                schema_name, Name
            ) and isinstance(table_name, Name):
                return InExpressionWithTableName(self_, schema_name, table_name)
            case _:
                assert all(
                    isinstance(e, Expression)
                    or e is None
                    or isinstance(e, (bool, int, float, str, bytes))
                    for e in exprs
                )
                exprs_ = typing.cast("tuple[ExpressionOrLiteral, ...]", exprs)
                coerced = tuple(_to_expr(e) for e in exprs_)
                return InExpressionWithExpressions(self_, coerced)

    def Glob(self, pattern: ExpressionOrLiteral) -> MatchLikeExpression:
        if isinstance(self, Expression):
            self_ = self._wrap_parenthesis_if_not(ComparisonPrecedence)
        else:
            self_ = self
        pattern_ = _to_expr(pattern)._wrap_parenthesis_if_not(RelationalPrecedence)
        return MatchLikeExpression(self_, pattern_, "GLOB")

    def Regexp(self, pattern: ExpressionOrLiteral) -> MatchLikeExpression:
        if isinstance(self, Expression):
            self_ = self._wrap_parenthesis_if_not(ComparisonPrecedence)
        else:
            self_ = self
        pattern_ = _to_expr(pattern)._wrap_parenthesis_if_not(RelationalPrecedence)
        return MatchLikeExpression(self_, pattern_, "REGEXP")

    def Match(self, pattern: ExpressionOrLiteral) -> MatchLikeExpression:
        if isinstance(self, Expression):
            self_ = self._wrap_parenthesis_if_not(ComparisonPrecedence)
        else:
            self_ = self
        pattern_ = _to_expr(pattern)._wrap_parenthesis_if_not(RelationalPrecedence)
        return MatchLikeExpression(self_, pattern_, "MATCH")

    def Like(self, pattern: ExpressionOrLiteral) -> LikeExpression:
        if isinstance(self, Expression):
            self_ = self._wrap_parenthesis_if_not(ComparisonPrecedence)
        else:
            self_ = self
        pattern_ = _to_expr(pattern)._wrap_parenthesis_if_not(RelationalPrecedence)
        return LikeExpression(self_, pattern_)


class Expression(IHasAscDesc, INegatedOperations, IHasFrameBounds, ABC):
    def As(self, alias: str | Name, /) -> AliasedExpression:
        if isinstance(alias, str):
            alias = Name(alias)
        return AliasedExpression(self, alias)

    def Or(self, other: ExpressionOrLiteral) -> OrCondition:
        self_ = self._wrap_parenthesis_if_not(OrPrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(AndPrecedence)
        return OrCondition(self_, other_)

    def And(self, other: ExpressionOrLiteral) -> AndCondition:
        self_ = self._wrap_parenthesis_if_not(AndPrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(NotPrecedence)
        return AndCondition(self_, other_)

    def eq(self, other: ExpressionOrLiteral, double_eq: bool = False) -> EqExpression:
        self_ = self._wrap_parenthesis_if_not(ComparisonPrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(RelationalPrecedence)
        return EqExpression(self_, other_, double_eq)

    def ne(self, other: ExpressionOrLiteral, arrows: bool = False) -> NeExpression:
        self_ = self._wrap_parenthesis_if_not(ComparisonPrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(RelationalPrecedence)
        return NeExpression(self_, other_, arrows)

    @override
    def __eq__(self, other: ExpressionOrLiteral) -> EqExpression:  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride] # ty: ignore[invalid-method-override]
        return self.eq(other)

    @override
    def __ne__(self, other: ExpressionOrLiteral) -> NeExpression:  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride] # ty: ignore[invalid-method-override]
        return self.ne(other)

    # Defining __eq__ would otherwise set __hash__ to None, making every
    # expression unhashable.
    __hash__ = object.__hash__

    def __bool__(self) -> NoReturn:
        # Comparison dunders build SQL instead of returning bool, so any
        # truth-test of an expression (`if a == b:`, `expr in a_list`,
        # `0 < col < 5`) would silently take the truthy branch. Fail loudly.
        raise TypeError("The boolean value of an Expression is not defined")

    @property
    def Is(self) -> IsExpression:
        self_ = self._wrap_parenthesis_if_not(ComparisonPrecedence)
        return IsExpression(self_)

    @property
    def IsNull(self) -> NullCompareExpression:
        self_ = self._wrap_parenthesis_if_not(ComparisonPrecedence)
        return NullCompareExpression(self_, "ISNULL")

    @property
    def Notnull(self) -> NullCompareExpression:
        self_ = self._wrap_parenthesis_if_not(ComparisonPrecedence)
        return NullCompareExpression(self_, "NOTNULL")

    @property
    def Not(self) -> NegatedOperator:
        self_ = self._wrap_parenthesis_if_not(ComparisonPrecedence)
        return NegatedOperator(self_)

    def __lt__(self, other: ExpressionOrLiteral) -> Comparison:
        self_ = self._wrap_parenthesis_if_not(RelationalPrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(EscapePrecedence)
        return Comparison(self_, other_, "<")

    def __le__(self, other: ExpressionOrLiteral) -> Comparison:
        self_ = self._wrap_parenthesis_if_not(RelationalPrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(EscapePrecedence)
        return Comparison(self_, other_, "<=")

    def __gt__(self, other: ExpressionOrLiteral) -> Comparison:
        self_ = self._wrap_parenthesis_if_not(RelationalPrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(EscapePrecedence)
        return Comparison(self_, other_, ">")

    def __ge__(self, other: ExpressionOrLiteral) -> Comparison:
        self_ = self._wrap_parenthesis_if_not(RelationalPrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(EscapePrecedence)
        return Comparison(self_, other_, ">=")

    def __and__(self, other: ExpressionOrLiteral) -> BitOperation:
        self_ = self._wrap_parenthesis_if_not(BitwisePrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(AdditivePrecedence)
        return BitOperation(self_, other_, "&")

    def __rand__(self, other: ExpressionOrLiteral) -> BitOperation:
        left_ = _to_expr(other)._wrap_parenthesis_if_not(BitwisePrecedence)
        right_ = self._wrap_parenthesis_if_not(AdditivePrecedence)
        return BitOperation(left_, right_, "&")

    def __or__(self, other: ExpressionOrLiteral) -> BitOperation:
        self_ = self._wrap_parenthesis_if_not(BitwisePrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(AdditivePrecedence)
        return BitOperation(self_, other_, "|")

    def __ror__(self, other: ExpressionOrLiteral) -> BitOperation:
        left_ = _to_expr(other)._wrap_parenthesis_if_not(BitwisePrecedence)
        right_ = self._wrap_parenthesis_if_not(AdditivePrecedence)
        return BitOperation(left_, right_, "|")

    def __lshift__(self, other: ExpressionOrLiteral) -> BitOperation:
        self_ = self._wrap_parenthesis_if_not(BitwisePrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(AdditivePrecedence)
        return BitOperation(self_, other_, "<<")

    def __rlshift__(self, other: ExpressionOrLiteral) -> BitOperation:
        left_ = _to_expr(other)._wrap_parenthesis_if_not(BitwisePrecedence)
        right_ = self._wrap_parenthesis_if_not(AdditivePrecedence)
        return BitOperation(left_, right_, "<<")

    def __rshift__(self, other: ExpressionOrLiteral) -> BitOperation:
        self_ = self._wrap_parenthesis_if_not(BitwisePrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(AdditivePrecedence)
        return BitOperation(self_, other_, ">>")

    def __rrshift__(self, other: ExpressionOrLiteral) -> BitOperation:
        left_ = _to_expr(other)._wrap_parenthesis_if_not(BitwisePrecedence)
        right_ = self._wrap_parenthesis_if_not(AdditivePrecedence)
        return BitOperation(left_, right_, ">>")

    def __add__(self, other: ExpressionOrLiteral) -> Summand:
        self_ = self._wrap_parenthesis_if_not(AdditivePrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(MultiplicativePrecedence)
        return Summand(self_, other_, "+")

    def __radd__(self, other: ExpressionOrLiteral) -> Summand:
        left_ = _to_expr(other)._wrap_parenthesis_if_not(AdditivePrecedence)
        right_ = self._wrap_parenthesis_if_not(MultiplicativePrecedence)
        return Summand(left_, right_, "+")

    def __sub__(self, other: ExpressionOrLiteral) -> Summand:
        self_ = self._wrap_parenthesis_if_not(AdditivePrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(MultiplicativePrecedence)
        return Summand(self_, other_, "-")

    def __rsub__(self, other: ExpressionOrLiteral) -> Summand:
        left_ = _to_expr(other)._wrap_parenthesis_if_not(AdditivePrecedence)
        right_ = self._wrap_parenthesis_if_not(MultiplicativePrecedence)
        return Summand(left_, right_, "-")

    def __mul__(self, other: ExpressionOrLiteral) -> Factor:
        self_ = self._wrap_parenthesis_if_not(MultiplicativePrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(ConcatPrecedence)
        return Factor(self_, other_, "*")

    def __rmul__(self, other: ExpressionOrLiteral) -> Factor:
        left_ = _to_expr(other)._wrap_parenthesis_if_not(MultiplicativePrecedence)
        right_ = self._wrap_parenthesis_if_not(ConcatPrecedence)
        return Factor(left_, right_, "*")

    def __truediv__(self, other: ExpressionOrLiteral) -> Factor:
        self_ = self._wrap_parenthesis_if_not(MultiplicativePrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(ConcatPrecedence)
        return Factor(self_, other_, "/")

    def __rtruediv__(self, other: ExpressionOrLiteral) -> Factor:
        left_ = _to_expr(other)._wrap_parenthesis_if_not(MultiplicativePrecedence)
        right_ = self._wrap_parenthesis_if_not(ConcatPrecedence)
        return Factor(left_, right_, "/")

    def __mod__(self, other: ExpressionOrLiteral) -> Factor:
        self_ = self._wrap_parenthesis_if_not(MultiplicativePrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(ConcatPrecedence)
        return Factor(self_, other_, "%")

    def __rmod__(self, other: ExpressionOrLiteral) -> Factor:
        left_ = _to_expr(other)._wrap_parenthesis_if_not(MultiplicativePrecedence)
        right_ = self._wrap_parenthesis_if_not(ConcatPrecedence)
        return Factor(left_, right_, "%")

    def Concat(self, other: ExpressionOrLiteral) -> ConcatLikeOperator:
        self_ = self._wrap_parenthesis_if_not(ConcatPrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(CollatePrecedence)
        return ConcatLikeOperator(self_, other_, "||")

    def Extract(self, other: ExpressionOrLiteral) -> ConcatLikeOperator:
        self_ = self._wrap_parenthesis_if_not(ConcatPrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(CollatePrecedence)
        return ConcatLikeOperator(self_, other_, "->")

    def Extract2(self, other: ExpressionOrLiteral) -> ConcatLikeOperator:
        self_ = self._wrap_parenthesis_if_not(ConcatPrecedence)
        other_ = _to_expr(other)._wrap_parenthesis_if_not(CollatePrecedence)
        return ConcatLikeOperator(self_, other_, "->>")

    def Collate(self, other: Name | str, /) -> CollateOperator:
        self_ = self._wrap_parenthesis_if_not(CollatePrecedence)
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


class OrPrecedence(Expression, ABC):
    """Precedence level 1 (lowest): OR."""


class OrCondition(OrPrecedence):
    def __init__(self, left: OrPrecedence, right: AndPrecedence) -> None:
        self._left = left
        self._right = right

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._left._create_query(buffer)
        buffer.append(" OR ")
        self._right._create_query(buffer)


class AndPrecedence(OrPrecedence, ABC):
    """Precedence level 2: AND."""


class AndCondition(AndPrecedence):
    def __init__(self, left: AndPrecedence, right: NotPrecedence) -> None:
        self._left = left
        self._right = right

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._left._create_query(buffer)
        buffer.append(" AND ")
        self._right._create_query(buffer)


class NotPrecedence(AndPrecedence, ABC):
    """Precedence level 3: NOT."""


class NotKeyword:
    def __call__(self, after: ExpressionOrLiteral) -> NotExpression:
        return NotExpression(_to_expr(after)._wrap_parenthesis_if_not(NotPrecedence))

    def Exists(self, select_stmt: SelectStatement) -> NotExpression:
        return NotExpression(Exists(select_stmt))


Not = NotKeyword()


class NotExpression(NotPrecedence):
    def __init__(self, after: NotPrecedence) -> None:
        self._after = after

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("NOT ")
        self._after._create_query(buffer)


class ComparisonPrecedence(NotPrecedence, ABC):
    """Precedence level 4: =, ==, !=, <>, IS, IN, LIKE, GLOB, MATCH, REGEXP, BETWEEN, ISNULL, NOTNULL."""


class EqExpression(ComparisonPrecedence):
    def __init__(
        self, left: ComparisonPrecedence, right: RelationalPrecedence, double_eq: bool
    ) -> None:
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


class NeExpression(ComparisonPrecedence):
    def __init__(
        self, left: ComparisonPrecedence, right: RelationalPrecedence, arrows: bool
    ) -> None:
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


class IsExpressionComplete(ComparisonPrecedence):
    def __init__(self, prev: IIsCallable, other: ComparisonPrecedence) -> None:
        self._prev = prev
        self._other = other

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._other._create_query(buffer)


class IIsCallable(SqlElement, ABC):
    def __call__(self, other: ExpressionOrLiteral) -> IsExpressionComplete:
        _other = _to_expr(other)._wrap_parenthesis_if_not(ComparisonPrecedence)
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
    def __init__(self, prev: ComparisonPrecedence) -> None:
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


class BetweenExpression(ComparisonPrecedence):
    def __init__(
        self, prev: SqlElement, lower: RelationalPrecedence, upper: RelationalPrecedence
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


class EmptyInExpression(ComparisonPrecedence):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IN ()")


class InExpressionWithSelect(ComparisonPrecedence):
    def __init__(self, prev: SqlElement, select_stmt: SelectStatement) -> None:
        self._prev = prev
        self._select_stmt = select_stmt

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IN (")
        self._select_stmt._create_query(buffer)
        buffer.append(")")


class InExpressionWithExpressions(ComparisonPrecedence):
    def __init__(self, prev: SqlElement, exprs: tuple[Expression, ...]) -> None:
        self._prev = prev
        self._exprs = exprs

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IN (")
        comma_separated(buffer, self._exprs)
        buffer.append(")")


class InExpressionWithTableName(ComparisonPrecedence):
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


class InExpressionWithTableFunction(ComparisonPrecedence):
    def __init__(self, prev: SqlElement, table_function: TableFunctionRefCall) -> None:
        self._prev = prev
        self._table_function = table_function

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IN ")
        self._table_function._create_query(buffer)


class MatchLikeExpression(ComparisonPrecedence):
    def __init__(
        self,
        prev: SqlElement,
        pattern: RelationalPrecedence,
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


class LikeExpressionWithEscape(ComparisonPrecedence):
    def __init__(self, prev: LikeExpression, escape: RelationalPrecedence) -> None:
        self._prev = prev
        self._escape = escape

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ESCAPE ")
        self._escape._create_query(buffer)


class LikeExpression(ComparisonPrecedence):
    def __init__(self, prev: SqlElement, pattern: RelationalPrecedence) -> None:
        self._prev = prev
        self._pattern = pattern

    def Escape(self, escape: ExpressionOrLiteral) -> LikeExpressionWithEscape:
        escape_ = _to_expr(escape)._wrap_parenthesis_if_not(RelationalPrecedence)
        return LikeExpressionWithEscape(self, escape_)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" LIKE ")
        self._pattern._create_query(buffer)


class NullCompareExpression(ComparisonPrecedence):
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
    def __init__(self, prev: ComparisonPrecedence) -> None:
        self._prev = prev

    @property
    def Null(self) -> NullCompareExpression:
        return NullCompareExpression(self, "NULL")

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" NOT")


class RelationalPrecedence(ComparisonPrecedence, ABC):
    """Precedence level 5: <, <=, >, >=."""


class Comparison(RelationalPrecedence):
    def __init__(
        self,
        left: RelationalPrecedence,
        right: EscapePrecedence,
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


class EscapePrecedence(RelationalPrecedence, ABC):
    """Precedence level 6: ESCAPE."""


class BitwisePrecedence(EscapePrecedence, ABC):
    """Precedence level 7: &, |, <<, >>."""


class BitOperation(BitwisePrecedence):
    def __init__(
        self,
        left: BitwisePrecedence,
        right: AdditivePrecedence,
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


class AdditivePrecedence(BitwisePrecedence, ABC):
    """Precedence level 8: +, -."""


class Summand(AdditivePrecedence):
    def __init__(
        self,
        left: AdditivePrecedence,
        right: MultiplicativePrecedence,
        operator: typing.Literal["+", "-"],
    ):
        self._left = left
        self._right = right
        self._operator = operator

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._left._create_query(buffer)
        buffer.append(f" {self._operator} ")
        self._right._create_query(buffer)


class MultiplicativePrecedence(AdditivePrecedence, ABC):
    """Precedence level 9: *, /, %."""


class Factor(MultiplicativePrecedence):
    def __init__(
        self,
        left: MultiplicativePrecedence,
        right: ConcatPrecedence,
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


class ConcatPrecedence(MultiplicativePrecedence, ABC):
    """Precedence level 10: ||, ->, ->>."""


class ConcatLikeOperator(ConcatPrecedence):
    def __init__(
        self,
        left: ConcatPrecedence,
        right: CollatePrecedence,
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


class CollatePrecedence(ConcatPrecedence, ABC):
    """Precedence level 11: COLLATE."""


class CollateOperator(CollatePrecedence):
    def __init__(
        self,
        left: CollatePrecedence,
        right: Name,
    ):
        self._left = left
        self._right = right

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._left._create_query(buffer)
        buffer.append(" COLLATE ")
        self._right._create_query(buffer)


class UnaryPrecedence(CollatePrecedence, ABC):
    """Precedence level 12: unary +, -, ~ and bind parameters."""


class UnaryOperator(UnaryPrecedence):
    def __init__(self, left: Expression, op: typing.Literal["+", "-", "~"]):
        self._left = left
        self._op = op

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append(self._op)
        self._left._create_query(buffer)


class PrimaryPrecedence(UnaryPrecedence, ABC):
    """Precedence level 13 (highest): literals, column names, function calls, parenthesized expressions."""


class ParenthesizedExpression(PrimaryPrecedence):
    def __init__(self, prev: Expression) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("(")
        self._prev._create_query(buffer)
        buffer.append(")")


class Row(PrimaryPrecedence):
    def __init__(
        self,
        *exprs: *tuple[
            ExpressionOrLiteral,
            ExpressionOrLiteral,
            *tuple[ExpressionOrLiteral, ...],
        ],
    ) -> None:
        self._exprs = tuple(_to_expr(e) for e in exprs)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("(")
        comma_separated(buffer, self._exprs)
        buffer.append(")")


class Cast(PrimaryPrecedence):
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


class ScalarSubquery(PrimaryPrecedence):
    def __init__(self, select_stmt: SelectStatement) -> None:
        self._select_stmt = select_stmt

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("(")
        self._select_stmt._create_query(buffer)
        buffer.append(")")


class Exists(PrimaryPrecedence):
    def __init__(self, select_stmt: SelectStatement) -> None:
        self._select_stmt = select_stmt

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("EXISTS (")
        self._select_stmt._create_query(buffer)
        buffer.append(")")


class RaiseExpression(PrimaryPrecedence):
    def __init__(
        self,
        mode: typing.Literal["IGNORE", "ROLLBACK", "ABORT", "FAIL"],
        message: Expression | None,
    ) -> None:
        self._mode = mode
        self._message = message

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append(f"RAISE({self._mode}")
        if self._message is not None:
            buffer.append(", ")
            self._message._create_query(buffer)
        buffer.append(")")


class RaiseKeyword:
    @overload
    def __call__(self, mode: typing.Literal["IGNORE"], /) -> RaiseExpression: ...
    @overload
    def __call__(
        self,
        mode: typing.Literal["ROLLBACK", "ABORT", "FAIL"],
        message: ExpressionOrLiteral,
        /,
    ) -> RaiseExpression: ...
    def __call__(
        self,
        mode: typing.Literal["IGNORE", "ROLLBACK", "ABORT", "FAIL"],
        message: ExpressionOrLiteral | NoArg = NoArg.NO_ARG,
        /,
    ) -> RaiseExpression:
        msg_expr = None if message is NoArg.NO_ARG else _to_expr(message)
        return RaiseExpression(mode, msg_expr)


Raise = RaiseKeyword()
