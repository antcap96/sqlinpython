from __future__ import annotations

from abc import ABC
from typing import Literal, override
import typing

from sqlinpython.base import SqlElement, comma_separated
from sqlinpython.expression.core import AliasedExpression, Expression
from sqlinpython.expression.function import Star_, WindowDefn
from sqlinpython.name import Name
from sqlinpython.ordering_term import OrderingTerm
from sqlinpython.select_base import Complete, Core, SelectStatement_
from sqlinpython.table_or_subquery import JoinClause, TableOrSubquery


# Result column types
# "* " is handled by the literal string "*"
# table-name.* is handled by TableStarResultColumn from table_or_subquery
ResultColumn = Expression | AliasedExpression | Star_

_ResultColumnArg = Literal["*"] | ResultColumn


def _resolve_result_column(arg: _ResultColumnArg) -> ResultColumn:
    from sqlinpython.expression.function import Star as StarSingleton

    if arg == "*":
        return StarSingleton
    return arg


# ---------------------------------------------------------------------------
# LIMIT / OFFSET
# ---------------------------------------------------------------------------


class SelectLimitOffset(SelectStatement_[Complete]):
    def __init__(self, prev: SqlElement, offset: Expression) -> None:
        self._prev = prev
        self._offset = offset

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" OFFSET ")
        self._offset._create_query(buffer)


class SelectLimit(SelectStatement_[Complete]):
    def __init__(self, prev: SqlElement, limit: Expression) -> None:
        self._prev = prev
        self._limit = limit

    def Offset(self, offset: Expression) -> SelectLimitOffset:
        return SelectLimitOffset(self, offset)

    def __call__(self, offset: Expression) -> SelectLimitOffset:
        """Comma syntax: LIMIT x, y (equivalent to LIMIT y OFFSET x)."""
        return SelectLimitOffset(self, offset)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" LIMIT ")
        self._limit._create_query(buffer)


# ---------------------------------------------------------------------------
# Mixin interfaces (define methods only, no _create_query)
# ---------------------------------------------------------------------------


class ISelectLimit(SqlElement, ABC):
    def Limit(self, expr: Expression) -> SelectLimit:
        return SelectLimit(self, expr)


class ISelectOrderBy(ISelectLimit, ABC):
    def OrderBy(self, *terms: OrderingTerm) -> SelectOrderBy:
        return SelectOrderBy(self, terms)


class ISelectCompound[T: Core | Complete](ISelectOrderBy, SelectStatement_[T], ABC):
    def Union(self, rhs: SelectStatement_[Core]) -> SelectCompound[T]:
        return SelectCompound(self, "UNION", rhs)

    def UnionAll(self, rhs: SelectStatement_[Core]) -> SelectCompound[T]:
        return SelectCompound(self, "UNION ALL", rhs)

    def Intersect(self, rhs: SelectStatement_[Core]) -> SelectCompound[T]:
        return SelectCompound(self, "INTERSECT", rhs)

    def Except(self, rhs: SelectStatement_[Core]) -> SelectCompound[T]:
        return SelectCompound(self, "EXCEPT", rhs)


class ISelectWindowClause[T: Core | Complete](ISelectCompound[T], ABC):
    def Window(self, *defs: tuple[Name | str, WindowDefn]) -> SelectWindowClause[T]:
        return SelectWindowClause(self, defs)


class ISelectHavingClause[T: Core | Complete](ISelectWindowClause[T], ABC):
    def Having(self, expr: Expression) -> SelectHavingClause[T]:
        return SelectHavingClause(self, expr)


class ISelectGroupByClause[T: Core | Complete](ISelectHavingClause[T], ABC):
    def GroupBy(self, *exprs: Expression) -> SelectGroupByClause[T]:
        return SelectGroupByClause(self, exprs)


class ISelectWhereClause[T: Core | Complete](ISelectGroupByClause[T], ABC):
    def Where(self, expr: Expression) -> SelectWhereClause[T]:
        return SelectWhereClause(self, expr)


class ISelectFromClause[T: Core | Complete](ISelectWhereClause[T], ABC):
    def From(self, *sources: TableOrSubquery | JoinClause) -> SelectFromClause[T]:
        if len(sources) == 1 and isinstance(sources[0], JoinClause):
            return SelectFromClause(self, sources[0])
        return SelectFromClause(self, sources)


# ---------------------------------------------------------------------------
# Concrete SELECT clause chain
# ---------------------------------------------------------------------------


class SelectColumns[T: Core | Complete](ISelectFromClause[T], SelectStatement_[T]):
    """SELECT [DISTINCT|ALL] col1, col2, ..."""

    def __init__(self, prev: SqlElement, cols: tuple[ResultColumn, ...]) -> None:
        self._prev = prev
        self._cols = cols

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        for i, col in enumerate(self._cols):
            if i > 0:
                buffer.append(", ")
            col._create_query(buffer)


class SelectFromClause[T: Core | Complete](ISelectWhereClause[T], SelectStatement_[T]):
    """... FROM source(s)"""

    def __init__(
        self, prev: SqlElement, source: JoinClause | tuple[TableOrSubquery, ...]
    ) -> None:
        self._prev = prev
        self._source = source

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" FROM ")
        if isinstance(self._source, JoinClause):
            self._source._create_query(buffer)
        else:
            comma_separated(buffer, self._source)


class SelectWhereClause[T: Core | Complete](ISelectGroupByClause[T], SelectStatement_[T]):
    """... WHERE expr"""

    def __init__(self, prev: SqlElement, expr: Expression) -> None:
        self._prev = prev
        self._expr = expr

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" WHERE ")
        self._expr._create_query(buffer)


class SelectGroupByClause[T: Core | Complete](ISelectHavingClause[T], SelectStatement_[T]):
    """... GROUP BY expr, ..."""

    def __init__(self, prev: SqlElement, exprs: tuple[Expression, ...]) -> None:
        self._prev = prev
        self._exprs = exprs

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" GROUP BY ")
        for i, expr in enumerate(self._exprs):
            if i > 0:
                buffer.append(", ")
            expr._create_query(buffer)


class SelectHavingClause[T: Core | Complete](ISelectWindowClause[T], SelectStatement_[T]):
    """... HAVING expr"""

    def __init__(self, prev: SqlElement, expr: Expression) -> None:
        self._prev = prev
        self._expr = expr

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" HAVING ")
        self._expr._create_query(buffer)


class SelectWindowClause[T: Core | Complete](ISelectCompound[T], SelectStatement_[T]):
    """... WINDOW name AS (window-defn), ..."""

    def __init__(
        self, prev: SqlElement, defs: tuple[tuple[Name | str, WindowDefn], ...]
    ) -> None:
        self._prev = prev
        self._defs = defs

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" WINDOW ")
        for i, (name, defn) in enumerate(self._defs):
            if i > 0:
                buffer.append(", ")
            if isinstance(name, str):
                Name(name)._create_query(buffer)
            else:
                name._create_query(buffer)
            buffer.append(" AS (")
            defn._create_query(buffer)
            buffer.append(")")


class SelectCompound[T: Core | Complete](ISelectCompound[T], SelectStatement_[T]):
    """... UNION/INTERSECT/EXCEPT select-stmt"""

    def __init__(
        self,
        prev: SqlElement,
        op: Literal["UNION", "UNION ALL", "INTERSECT", "EXCEPT"],
        rhs: SelectStatement_[Core],
    ) -> None:
        self._prev = prev
        self._op = op
        self._rhs = rhs

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._op} ")
        self._rhs._create_query(buffer)


class SelectOrderBy(ISelectLimit, SelectStatement_[Complete]):
    """... ORDER BY term, ..."""

    def __init__(self, prev: SqlElement, terms: tuple[OrderingTerm, ...]) -> None:
        self._prev = prev
        self._terms = terms

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ORDER BY ")
        for i, term in enumerate(self._terms):
            if i > 0:
                buffer.append(", ")
            term._create_query(buffer)


class SelectValues[T: Core | Complete](ISelectOrderBy, SelectStatement_[T]):
    """VALUES (expr, ...), ..."""

    def __init__(
        self, prev: SqlElement, rows: tuple[tuple[Expression, ...], ...]
    ) -> None:
        self._prev = prev
        self._rows = rows

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        for i, row in enumerate(self._rows):
            if i > 0:
                buffer.append(", ")
            buffer.append("(")
            for j, expr in enumerate(row):
                if j > 0:
                    buffer.append(", ")
                expr._create_query(buffer)
            buffer.append(")")


# ---------------------------------------------------------------------------
# Entry point keywords
# ---------------------------------------------------------------------------


class SelectDistinctKeyword[T: Core | Complete](SqlElement):
    """SELECT DISTINCT — awaiting result columns."""

    def __init__(self, prev: SelectKeyword[T]) -> None:
        self._prev = prev

    def __call__(self, *cols: _ResultColumnArg) -> SelectColumns[T]:
        resolved = tuple(_resolve_result_column(c) for c in cols)
        return SelectColumns(self, resolved)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" DISTINCT")


class SelectAllKeyword[T: Core | Complete](SqlElement):
    """SELECT ALL — awaiting result columns."""

    def __init__(self, prev: SelectKeyword[T]) -> None:
        self._prev = prev

    def __call__(self, *cols: _ResultColumnArg) -> SelectColumns[T]:
        resolved = tuple(_resolve_result_column(c) for c in cols)
        return SelectColumns(self, resolved)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ALL")


class SelectKeyword[T: Core | Complete](SqlElement):
    """SELECT keyword — entry point for SELECT statements."""

    @typing.overload
    def __init__(self: SelectKeyword[Core], prev: None = None) -> None: ...
    @typing.overload
    def __init__(self: SelectKeyword[Complete], prev: SqlElement) -> None: ...
    def __init__(self, prev: SqlElement | None = None) -> None:
        self._prev = prev

    @property
    def Distinct(self) -> SelectDistinctKeyword[T]:
        return SelectDistinctKeyword(self)

    @property
    def All(self) -> SelectAllKeyword[T]:
        return SelectAllKeyword(self)

    def __call__(self, *cols: _ResultColumnArg) -> SelectColumns[T]:
        resolved = tuple(_resolve_result_column(c) for c in cols)
        return SelectColumns(self, resolved)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        if self._prev is not None:
            self._prev._create_query(buffer)
            buffer.append(" ")
        buffer.append("SELECT")


class ValuesKeyword[T: Core | Complete](SqlElement):
    """VALUES keyword — entry point for VALUES statements."""

    @typing.overload
    def __init__(self: ValuesKeyword[Core], prev: None = None) -> None: ...
    @typing.overload
    def __init__(self: ValuesKeyword[Complete], prev: SqlElement) -> None: ...
    def __init__(self, prev: SqlElement | None = None) -> None:
        self._prev = prev

    def __call__(self, *rows: tuple[Expression, ...]) -> SelectValues[T]:
        return SelectValues(self, rows)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        if self._prev is not None:
            self._prev._create_query(buffer)
            buffer.append(" ")
        buffer.append("VALUES")


# Entry point singletons
Select = SelectKeyword()
Values = ValuesKeyword()
