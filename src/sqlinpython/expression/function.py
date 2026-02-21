from __future__ import annotations

from typing import Literal, cast, overload

from sqlinpython.base import SqlElement
from sqlinpython.name import Name
from sqlinpython.ordering_term import OrderingTerm

from .core import Expression, Expression13


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

    def _create_query(self, buffer: list[str]) -> None:
        if self._prev is not None:
            self._prev._create_query(buffer)
            buffer.append(" ")
        buffer.append("ORDER BY ")
        for i, term in enumerate(self._terms):
            if i > 0:
                buffer.append(", ")
            term._create_query(buffer)


class PartitionByKeyword:
    def __init__(self, prev: SqlElement | None):
        self._prev = prev

    def __call__(self, first_expr: Expression, *exprs: Expression) -> PartitionByClause:
        return PartitionByClause(self._prev, (first_expr, *exprs))


PartitionBy = PartitionByKeyword(None)


class PartitionByClause(WindowDefn):
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
