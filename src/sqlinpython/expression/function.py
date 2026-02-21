from __future__ import annotations

from typing import Literal, cast, overload

from sqlinpython.base import SqlElement
from sqlinpython.name import Name
from sqlinpython.ordering_term import OrderingTerm

from .core import Expression, Expression13, FollowingFrameBound, PrecedingFrameBound


class _Star(SqlElement):
    """Represents * in function arguments like COUNT(*)."""

    def __init__(self) -> None:
        pass

    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("*")


Star = _Star()


class FunctionName(SqlElement):
    """A SQL function name that can be called with arguments."""

    def __init__(self, name: str) -> None:
        self._name = Name(name)

    @overload
    def __call__(self) -> FunctionCall: ...

    @overload
    def __call__(self, __star: Literal["*"] | _Star) -> FunctionCall: ...

    @overload
    def __call__(
        self,
        __first: Expression,
        *rest: Expression,
        distinct: bool = False,
        order_by: tuple[OrderingTerm, ...] | None = None,
    ) -> FunctionCall: ...

    def __call__(
        self,
        *args: Literal["*"] | _Star | Expression,
        distinct: bool = False,
        order_by: tuple[OrderingTerm, ...] | None = None,
    ) -> FunctionCall:
        match args:
            case ():
                return FunctionCall(self, (), distinct=distinct, order_by=order_by)
            case ("*",) | (_Star(),):
                return FunctionCall(self, (), star=True)
            case _:
                # Cast is safe here: the previous cases handle "*" and _Star,
                # so remaining args can only be Expression instances.
                return FunctionCall(
                    self,
                    cast(tuple[Expression, ...], args),
                    distinct=distinct,
                    order_by=order_by,
                )

    def _create_query(self, buffer: list[str]) -> None:
        self._name._create_query(buffer)


class WindowDefn(SqlElement):
    pass


class OrderByKeyword:
    def __init__(self, prev: SqlElement | None):
        self._prev = prev

    def __call__(self, first_term: OrderingTerm, *terms: OrderingTerm) -> OrderByClause:
        return OrderByClause(self._prev, (first_term, *terms))


OrderBy = OrderByKeyword(None)


class OrderByClause(WindowDefn):
    def __init__(self, prev: SqlElement | None, terms: tuple[OrderingTerm, ...]):
        self._prev = prev
        self._terms = terms

    @property
    def Range(self) -> FrameSpecClause:
        return FrameSpecClause(self, "RANGE")

    @property
    def Rows(self) -> FrameSpecClause:
        return FrameSpecClause(self, "ROWS")

    @property
    def Groups(self) -> FrameSpecClause:
        return FrameSpecClause(self, "GROUPS")

    def _create_query(self, buffer: list[str]) -> None:
        if self._prev is not None:
            self._prev._create_query(buffer)
            buffer.append(" ")
        buffer.append("ORDER BY ")
        for i, term in enumerate(self._terms):
            if i > 0:
                buffer.append(", ")
            term._create_query(buffer)


class FrameSpecClause(SqlElement):
    def __init__(
        self, prev: SqlElement | None, kind: Literal["RANGE", "ROWS", "GROUPS"]
    ):
        self._prev = prev
        self._kind = kind

    def __call__(self, bound: PrecedingFrameBound) -> FrameSpecExprBound:
        return FrameSpecExprBound(self, bound)

    @property
    def CurrentRow(self) -> FrameSpecSingleBound:
        return FrameSpecSingleBound(self, "CURRENT ROW")

    @property
    def UnboundedPreceding(self) -> FrameSpecSingleBound:
        return FrameSpecSingleBound(self, "UNBOUNDED PRECEDING")

    @property
    def Between(self) -> FrameSpecBetween:
        return FrameSpecBetween(self)

    def _create_query(self, buffer: list[str]) -> None:
        if self._prev is not None:
            self._prev._create_query(buffer)
            buffer.append(" ")
        buffer.append(self._kind)


class FrameSpecBetween(SqlElement):
    def __init__(self, prev: FrameSpecClause) -> None:
        self._prev = prev

    def __call__(
        self, bound: PrecedingFrameBound | FollowingFrameBound
    ) -> FrameSpecBetweenExprStart:
        return FrameSpecBetweenExprStart(self, bound)

    @property
    def UnboundedPreceding(self) -> FrameSpecBetweenStart:
        return FrameSpecBetweenStart(self, "UNBOUNDED PRECEDING")

    @property
    def CurrentRow(self) -> FrameSpecBetweenStart:
        return FrameSpecBetweenStart(self, "CURRENT ROW")

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" BETWEEN")


class FrameSpecBetweenExprStart(SqlElement):
    def __init__(
        self, prev: FrameSpecBetween, bound: PrecedingFrameBound | FollowingFrameBound
    ) -> None:
        self._prev = prev
        self._bound = bound

    @property
    def And(self) -> FrameSpecBetweenAnd:
        return FrameSpecBetweenAnd(self)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._bound._create_query(buffer)


class FrameSpecBetweenStart(SqlElement):
    def __init__(
        self,
        prev: FrameSpecBetween,
        kind: Literal["UNBOUNDED PRECEDING", "CURRENT ROW"],
    ) -> None:
        self._prev = prev
        self._kind = kind

    @property
    def And(self) -> FrameSpecBetweenAnd:
        return FrameSpecBetweenAnd(self)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        buffer.append(self._kind)


class FrameSpecBetweenAnd(SqlElement):
    def __init__(self, prev: FrameSpecBetweenStart | FrameSpecBetweenExprStart) -> None:
        self._prev = prev

    def __call__(
        self, bound: PrecedingFrameBound | FollowingFrameBound
    ) -> FrameSpecBetweenExprEnd:
        return FrameSpecBetweenExprEnd(self, bound)

    @property
    def UnboundedFollowing(self) -> FrameSpecBetweenEnd:
        return FrameSpecBetweenEnd(self, "UNBOUNDED FOLLOWING")

    @property
    def CurrentRow(self) -> FrameSpecBetweenEnd:
        return FrameSpecBetweenEnd(self, "CURRENT ROW")

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" AND")


class FrameSpecWithExclude(WindowDefn):
    def __init__(
        self,
        prev: SqlElement,
        kind: Literal["NO OTHERS", "CURRENT ROW", "GROUP", "TIES"],
    ) -> None:
        self._prev = prev
        self._kind = kind

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" EXCLUDE ")
        buffer.append(self._kind)


class FrameSpecBound(FrameSpecWithExclude):
    @property
    def ExcludeNoOthers(self) -> FrameSpecWithExclude:
        return FrameSpecWithExclude(self, "NO OTHERS")

    @property
    def ExcludeCurrentRow(self) -> FrameSpecWithExclude:
        return FrameSpecWithExclude(self, "CURRENT ROW")

    @property
    def ExcludeGroup(self) -> FrameSpecWithExclude:
        return FrameSpecWithExclude(self, "GROUP")

    @property
    def ExcludeTies(self) -> FrameSpecWithExclude:
        return FrameSpecWithExclude(self, "TIES")


class FrameSpecBetweenEnd(FrameSpecBound):
    def __init__(
        self,
        prev: FrameSpecBetweenAnd,
        kind: Literal["UNBOUNDED FOLLOWING", "CURRENT ROW"],
    ) -> None:
        self._prev = prev
        self._kind = kind  # type: ignore[assignment]

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        buffer.append(self._kind)


class FrameSpecBetweenExprEnd(FrameSpecBound):
    def __init__(
        self,
        prev: FrameSpecBetweenAnd,
        bound: PrecedingFrameBound | FollowingFrameBound,
    ) -> None:
        self._prev = prev
        self._bound = bound

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._bound._create_query(buffer)


class FrameSpecExprBound(FrameSpecBound):
    def __init__(self, prev: FrameSpecClause, bound: PrecedingFrameBound) -> None:
        self._prev = prev
        self._bound = bound

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._bound._create_query(buffer)


class FrameSpecSingleBound(FrameSpecBound):
    def __init__(
        self,
        prev: FrameSpecClause,
        kind: Literal["CURRENT ROW", "UNBOUNDED PRECEDING"],
    ) -> None:
        self._prev = prev
        self._kind = kind  # type: ignore[assignment]

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        buffer.append(self._kind)


Range = FrameSpecClause(None, "RANGE")
Rows = FrameSpecClause(None, "ROWS")
Groups = FrameSpecClause(None, "GROUPS")


class PartitionByKeyword:
    def __init__(self, prev: SqlElement | None):
        self._prev = prev

    def __call__(self, first_expr: Expression, *exprs: Expression) -> PartitionByClause:
        return PartitionByClause(self._prev, (first_expr, *exprs))


PartitionBy = PartitionByKeyword(None)


class PartitionByClause(OrderByClause):
    def __init__(self, prev: SqlElement | None, exprs: tuple[Expression, ...]):
        self._prev = prev
        self._exprs = exprs

    @property
    def OrderBy(self) -> OrderByKeyword:
        return OrderByKeyword(self)

    def _create_query(self, buffer: list[str]) -> None:
        if self._prev is not None:
            self._prev._create_query(buffer)
            buffer.append(" ")
        buffer.append("PARTITION BY ")
        for i, term in enumerate(self._exprs):
            if i > 0:
                buffer.append(", ")
            term._create_query(buffer)


class WindowName(Name, PartitionByClause):
    @property
    def PartitionBy(self) -> PartitionByKeyword:
        return PartitionByKeyword(self)


class FunctionCallWithOver(Expression13):
    def __init__(
        self, prev: SqlElement, arg: WindowName | WindowDefn | None = None, /
    ) -> None:
        self._prev = prev
        self._arg = arg

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" OVER ")
        if self._arg is None:
            buffer.append("()")
        elif type(self._arg) is WindowName:
            self._arg._create_query(buffer)
        else:
            buffer.append("(")
            self._arg._create_query(buffer)
            buffer.append(")")


class FunctionCallWithFilter(FunctionCallWithOver):
    """A function call with a FILTER clause."""

    def __init__(self, prev: FunctionCall, filter_expr: Expression) -> None:
        self._prev = prev
        self._filter_expr = filter_expr

    def Over(self, arg: WindowName | WindowDefn | None = None) -> FunctionCallWithOver:
        return FunctionCallWithOver(self, arg)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" FILTER (WHERE ")
        self._filter_expr._create_query(buffer)
        buffer.append(")")


class FunctionCall(FunctionCallWithFilter):
    """A complete function call with arguments."""

    def __init__(
        self,
        func: FunctionName,
        args: tuple[Expression, ...],
        star: bool = False,
        distinct: bool = False,
        order_by: tuple[OrderingTerm, ...] | None = None,
    ) -> None:
        self._func = func
        self._args = args
        self._star = star
        self._distinct = distinct
        self._order_by = order_by

    def _create_query(self, buffer: list[str]) -> None:
        self._func._create_query(buffer)
        buffer.append("(")
        if self._star:
            buffer.append("*")
        else:
            if self._distinct:
                buffer.append("DISTINCT ")
            for i, arg in enumerate(self._args):
                if i > 0:
                    buffer.append(", ")
                arg._create_query(buffer)
            if self._order_by:
                buffer.append(" ORDER BY ")
                for i, term in enumerate(self._order_by):
                    if i > 0:
                        buffer.append(", ")
                    term._create_query(buffer)
        buffer.append(")")

    def FilterWhere(self, expr: Expression) -> FunctionCallWithFilter:
        return FunctionCallWithFilter(self, expr)
