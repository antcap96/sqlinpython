from __future__ import annotations

import typing
from abc import ABC
from typing import Generic, Literal, override

from sqlinpython.base import NoArg, SqlElement, comma_separated
from sqlinpython.expression import (
    AliasedExpression,
    Expression,
    ExpressionOrLiteral,
    Star_,
    WindowDefn,
    to_expr,
)
from sqlinpython.name import Name
from sqlinpython.ordering_term import OrderingTerm
from sqlinpython.select_base import Complete, Core, SelectStatement_, T_co
from sqlinpython.table_or_subquery import (
    JoinClause,
    Subquery,
    SubqueryAliased,
    TableOrSubquery,
    TableStarResultColumn,
)

# SPEC: https://sqlite.org/lang_select.html

# Result column types
# "* " is handled by the literal string "*"
# table-name.* is handled by TableStarResultColumn from table_or_subquery
ResultColumn = Expression | AliasedExpression | Star_ | TableStarResultColumn

# "*" is the Star sentinel; bare literals become Literal expressions via to_expr.
# ExpressionOrLiteral already covers Expression and str (so "*" is covered by str).
_ResultColumnArg = (
    ExpressionOrLiteral | AliasedExpression | Star_ | TableStarResultColumn
)


def _resolve_result_column(arg: _ResultColumnArg) -> ResultColumn:
    from sqlinpython.expression import Star as StarSingleton

    if arg == "*":
        return StarSingleton
    if isinstance(arg, (Expression, AliasedExpression, Star_, TableStarResultColumn)):
        return arg
    return to_expr(arg)


class ISelectAliasable(SelectStatement_[Complete], ABC):
    """Mixin for SELECT statements that can be aliased as subqueries."""

    def As(self, alias: Name | str, *, explicit_as: bool = True) -> SubqueryAliased:
        if isinstance(alias, str):
            alias = Name(alias)
        return SubqueryAliased(self, alias, explicit_as)


# ---------------------------------------------------------------------------
# LIMIT / OFFSET
# ---------------------------------------------------------------------------


class SelectLimitOffset(ISelectAliasable):
    def __init__(self, prev: SqlElement, offset: Expression) -> None:
        self._prev = prev
        self._offset = offset

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" OFFSET ")
        self._offset._create_query(buffer)


class SelectLimitComma(ISelectAliasable):
    def __init__(self, prev: SqlElement, limit: Expression, offset: Expression) -> None:
        self._prev = prev
        self._limit = limit
        self._offset = offset

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" LIMIT ")
        self._limit._create_query(buffer)
        buffer.append(", ")
        self._offset._create_query(buffer)


class SelectLimit(ISelectAliasable):
    def __init__(self, prev: SqlElement, limit: Expression) -> None:
        self._prev = prev
        self._limit = limit

    def Offset(self, offset: ExpressionOrLiteral) -> SelectLimitOffset:
        return SelectLimitOffset(self, to_expr(offset))

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" LIMIT ")
        self._limit._create_query(buffer)


# ---------------------------------------------------------------------------
# Concrete SELECT clause chain
# ---------------------------------------------------------------------------


class ISelectLimit(SqlElement, ABC):
    @typing.overload
    def Limit(self, expr: ExpressionOrLiteral) -> SelectLimit: ...
    @typing.overload
    def Limit(
        self, expr: ExpressionOrLiteral, offset: ExpressionOrLiteral
    ) -> SelectLimitComma: ...
    def Limit(
        self,
        expr: ExpressionOrLiteral,
        offset: ExpressionOrLiteral | NoArg = NoArg.NO_ARG,
    ) -> SelectLimit | SelectLimitComma:
        if offset is NoArg.NO_ARG:
            return SelectLimit(self, to_expr(expr))
        return SelectLimitComma(self, to_expr(expr), to_expr(offset))


class SelectOrderBy(ISelectLimit, SelectStatement_[Complete]):
    """... ORDER BY term, ..."""

    def __init__(self, prev: SqlElement, terms: tuple[OrderingTerm, ...]) -> None:
        self._prev = prev
        self._terms = terms

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ORDER BY ")
        comma_separated(buffer, self._terms)


class ISelectOrderBy(ISelectLimit, ABC):
    def OrderBy(self, *terms: OrderingTerm) -> SelectOrderBy:
        return SelectOrderBy(self, terms)


class ISelectCompound(ISelectOrderBy, SelectStatement_[T_co], ABC):
    def Union(self, rhs: SelectStatement_[Core]) -> SelectCompound[T_co]:
        return SelectCompound(self, "UNION", rhs)

    def UnionAll(self, rhs: SelectStatement_[Core]) -> SelectCompound[T_co]:
        return SelectCompound(self, "UNION ALL", rhs)

    def Intersect(self, rhs: SelectStatement_[Core]) -> SelectCompound[T_co]:
        return SelectCompound(self, "INTERSECT", rhs)

    def Except(self, rhs: SelectStatement_[Core]) -> SelectCompound[T_co]:
        return SelectCompound(self, "EXCEPT", rhs)


class SelectValues(ISelectCompound[T_co], SelectStatement_[T_co]):
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
            comma_separated(buffer, row)
            buffer.append(")")


class SelectCompound(ISelectCompound[T_co], SelectStatement_[T_co]):
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


class SelectWindowClause(ISelectCompound[T_co], SelectStatement_[T_co]):
    """... WINDOW name AS (window-defn), ..."""

    def __init__(
        self, prev: SqlElement, defs: tuple[tuple[Name, WindowDefn], ...]
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
            name._create_query(buffer)
            buffer.append(" AS (")
            defn._create_query(buffer)
            buffer.append(")")


class ISelectWindowClause(ISelectCompound[T_co], ABC):
    def Window(self, *defs: tuple[Name | str, WindowDefn]) -> SelectWindowClause[T_co]:
        defs_names = tuple(
            (Name(name) if isinstance(name, str) else name, defn) for name, defn in defs
        )
        return SelectWindowClause(self, defs_names)


class SelectHavingClause(ISelectWindowClause[T_co], SelectStatement_[T_co]):
    """... HAVING expr"""

    def __init__(self, prev: SqlElement, expr: Expression) -> None:
        self._prev = prev
        self._expr = expr

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" HAVING ")
        self._expr._create_query(buffer)


class ISelectHavingClause(ISelectWindowClause[T_co], ABC):
    def Having(self, expr: ExpressionOrLiteral) -> SelectHavingClause[T_co]:
        return SelectHavingClause(self, to_expr(expr))


class SelectGroupByClause(ISelectHavingClause[T_co], SelectStatement_[T_co]):
    """... GROUP BY expr, ..."""

    def __init__(self, prev: SqlElement, exprs: tuple[Expression, ...]) -> None:
        self._prev = prev
        self._exprs = exprs

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" GROUP BY ")
        comma_separated(buffer, self._exprs)


class ISelectGroupByClause(ISelectHavingClause[T_co], ABC):
    def GroupBy(self, *exprs: ExpressionOrLiteral) -> SelectGroupByClause[T_co]:
        return SelectGroupByClause(self, tuple(to_expr(e) for e in exprs))


class SelectWhereClause(ISelectGroupByClause[T_co], SelectStatement_[T_co]):
    """... WHERE expr"""

    def __init__(self, prev: SqlElement, expr: Expression) -> None:
        self._prev = prev
        self._expr = expr

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" WHERE ")
        self._expr._create_query(buffer)


class ISelectWhereClause(ISelectGroupByClause[T_co], ABC):
    def Where(self, expr: ExpressionOrLiteral) -> SelectWhereClause[T_co]:
        return SelectWhereClause(self, to_expr(expr))


class SelectFromClause(ISelectWhereClause[T_co], SelectStatement_[T_co]):
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


class ISelectFromClause(ISelectWhereClause[T_co], ABC):
    def From(
        self, *sources: TableOrSubquery | JoinClause | SelectStatement_[Complete]
    ) -> SelectFromClause[T_co]:
        resolved = tuple(
            s if isinstance(s, (TableOrSubquery, JoinClause)) else Subquery(s)
            for s in sources
        )
        if len(resolved) == 1 and isinstance(resolved[0], JoinClause):
            return SelectFromClause(self, resolved[0])
        return SelectFromClause(self, resolved)


class SelectColumns(ISelectFromClause[T_co], SelectStatement_[T_co]):
    """SELECT [DISTINCT|ALL] col1, col2, ..."""

    def __init__(self, prev: SqlElement, cols: tuple[ResultColumn, ...]) -> None:
        self._prev = prev
        self._cols = cols

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        comma_separated(buffer, self._cols)


# ---------------------------------------------------------------------------
# Entry point keywords
# ---------------------------------------------------------------------------


class SelectDistinctKeyword(SqlElement, Generic[T_co]):
    """SELECT DISTINCT — awaiting result columns."""

    def __init__(self, prev: SelectKeyword[T_co]) -> None:
        self._prev = prev

    def __call__(self, *cols: _ResultColumnArg) -> SelectColumns[T_co]:
        resolved = tuple(_resolve_result_column(c) for c in cols)
        return SelectColumns(self, resolved)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" DISTINCT")


class SelectAllKeyword(SqlElement, Generic[T_co]):
    """SELECT ALL — awaiting result columns."""

    def __init__(self, prev: SelectKeyword[T_co]) -> None:
        self._prev = prev

    def __call__(self, *cols: _ResultColumnArg) -> SelectColumns[T_co]:
        resolved = tuple(_resolve_result_column(c) for c in cols)
        return SelectColumns(self, resolved)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ALL")


class SelectKeyword(SqlElement, Generic[T_co]):
    """SELECT keyword — entry point for SELECT statements."""

    @typing.overload
    def __init__(self: SelectKeyword[Core], prev: None = None) -> None: ...
    @typing.overload
    def __init__(self: SelectKeyword[Complete], prev: SqlElement) -> None: ...
    def __init__(self, prev: SqlElement | None = None) -> None:
        self._prev = prev

    @property
    def Distinct(self) -> SelectDistinctKeyword[T_co]:
        return SelectDistinctKeyword(self)

    @property
    def All(self) -> SelectAllKeyword[T_co]:
        return SelectAllKeyword(self)

    def __call__(self, *cols: _ResultColumnArg) -> SelectColumns[T_co]:
        resolved = tuple(_resolve_result_column(c) for c in cols)
        return SelectColumns(self, resolved)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        if self._prev is not None:
            self._prev._create_query(buffer)
            buffer.append(" ")
        buffer.append("SELECT")


class ValuesKeyword(SqlElement, Generic[T_co]):
    """VALUES keyword — entry point for VALUES statements."""

    @typing.overload
    def __init__(self: ValuesKeyword[Core], prev: None = None) -> None: ...
    @typing.overload
    def __init__(self: ValuesKeyword[Complete], prev: SqlElement) -> None: ...
    def __init__(self, prev: SqlElement | None = None) -> None:
        self._prev = prev

    def __call__(self, *rows: tuple[ExpressionOrLiteral, ...]) -> SelectValues[T_co]:
        return SelectValues(self, tuple(tuple(to_expr(e) for e in row) for row in rows))

    @override
    def _create_query(self, buffer: list[str]) -> None:
        if self._prev is not None:
            self._prev._create_query(buffer)
            buffer.append(" ")
        buffer.append("VALUES")


# Entry point singletons
Select = SelectKeyword()
Values = ValuesKeyword()
