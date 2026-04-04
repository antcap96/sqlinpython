from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, override

from sqlinpython.base import SqlElement, comma_separated
from sqlinpython.name import Name

if TYPE_CHECKING:
    from sqlinpython.select_base import SelectStatement


# SPEC: https://sqlite.org/syntax/table-or-subquery.html
# SPEC: https://sqlite.org/syntax/join-clause.html


class TableOrSubquery(SqlElement, ABC):
    """Base class for all table-or-subquery variants. Provides join methods."""

    def Join(self, rhs: TableOrSubquery) -> JoinRhs:
        return JoinRhs(self, " JOIN", rhs)

    def LeftJoin(self, rhs: TableOrSubquery) -> JoinRhs:
        return JoinRhs(self, " LEFT JOIN", rhs)

    def LeftOuterJoin(self, rhs: TableOrSubquery) -> JoinRhs:
        return JoinRhs(self, " LEFT OUTER JOIN", rhs)

    def RightJoin(self, rhs: TableOrSubquery) -> JoinRhs:
        return JoinRhs(self, " RIGHT JOIN", rhs)

    def RightOuterJoin(self, rhs: TableOrSubquery) -> JoinRhs:
        return JoinRhs(self, " RIGHT OUTER JOIN", rhs)

    def FullJoin(self, rhs: TableOrSubquery) -> JoinRhs:
        return JoinRhs(self, " FULL JOIN", rhs)

    def FullOuterJoin(self, rhs: TableOrSubquery) -> JoinRhs:
        return JoinRhs(self, " FULL OUTER JOIN", rhs)

    def InnerJoin(self, rhs: TableOrSubquery) -> JoinRhs:
        return JoinRhs(self, " INNER JOIN", rhs)

    def CrossJoin(self, rhs: TableOrSubquery) -> JoinRhs:
        return JoinRhs(self, " CROSS JOIN", rhs)

    def NaturalJoin(self, rhs: TableOrSubquery) -> JoinClause:
        return JoinClause(JoinRhsNoConstraint(self, " NATURAL JOIN", rhs))

    def NaturalLeftJoin(self, rhs: TableOrSubquery) -> JoinClause:
        return JoinClause(JoinRhsNoConstraint(self, " NATURAL LEFT JOIN", rhs))

    def NaturalLeftOuterJoin(self, rhs: TableOrSubquery) -> JoinClause:
        return JoinClause(JoinRhsNoConstraint(self, " NATURAL LEFT OUTER JOIN", rhs))

    def NaturalRightJoin(self, rhs: TableOrSubquery) -> JoinClause:
        return JoinClause(JoinRhsNoConstraint(self, " NATURAL RIGHT JOIN", rhs))

    def NaturalRightOuterJoin(self, rhs: TableOrSubquery) -> JoinClause:
        return JoinClause(JoinRhsNoConstraint(self, " NATURAL RIGHT OUTER JOIN", rhs))

    def NaturalFullJoin(self, rhs: TableOrSubquery) -> JoinClause:
        return JoinClause(JoinRhsNoConstraint(self, " NATURAL FULL JOIN", rhs))

    def NaturalFullOuterJoin(self, rhs: TableOrSubquery) -> JoinClause:
        return JoinClause(JoinRhsNoConstraint(self, " NATURAL FULL OUTER JOIN", rhs))

    def NaturalInnerJoin(self, rhs: TableOrSubquery) -> JoinClause:
        return JoinClause(JoinRhsNoConstraint(self, " NATURAL INNER JOIN", rhs))


class TableStarResultColumn(SqlElement):
    """Represents table-name.* in result columns."""

    def __init__(self, table_name: Name) -> None:
        self._table_name = table_name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._table_name._create_query(buffer)
        buffer.append(".*")


class TableRefAliased(TableOrSubquery):
    def __init__(self, prev: SqlElement, alias: Name) -> None:
        self._prev = prev
        self._alias = alias

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" AS ")
        self._alias._create_query(buffer)


class TableRefIndexedBy(TableOrSubquery):
    def __init__(self, prev: SqlElement, index_name: Name) -> None:
        self._prev = prev
        self._index_name = index_name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" INDEXED BY ")
        self._index_name._create_query(buffer)


class TableRefIndexedByKeyword(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def __call__(self, index_name: Name | str) -> TableRefIndexedBy:
        if isinstance(index_name, str):
            index_name = Name(index_name)
        return TableRefIndexedBy(self._prev, index_name)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" INDEXED BY")


class TableRefNotIndexed(TableOrSubquery):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" NOT INDEXED")


class TableRef(TableOrSubquery):
    """Represents [schema.]table-name in a FROM clause."""

    def __init__(self, name: Name | str, schema: Name | str | None = None) -> None:
        if isinstance(name, str):
            name = Name(name)
        if isinstance(schema, str):
            schema = Name(schema)
        self._name = name
        self._schema = schema

    def As(self, alias: Name | str) -> TableRefAliased:
        if isinstance(alias, str):
            alias = Name(alias)
        return TableRefAliased(self, alias)

    @property
    def IndexedBy(self) -> TableRefIndexedByKeyword:
        return TableRefIndexedByKeyword(self)

    @property
    def NotIndexed(self) -> TableRefNotIndexed:
        return TableRefNotIndexed(self)

    @property
    def Star(self) -> TableStarResultColumn:
        return TableStarResultColumn(self._name)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        if self._schema is not None:
            self._schema._create_query(buffer)
            buffer.append(".")
        self._name._create_query(buffer)


class TableFunctionRefAliased(TableOrSubquery):
    def __init__(self, prev: SqlElement, alias: Name) -> None:
        self._prev = prev
        self._alias = alias

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" AS ")
        self._alias._create_query(buffer)


class TableFunctionRefCall(TableOrSubquery):
    def __init__(self, prev: SqlElement, args: tuple[SqlElement, ...]) -> None:
        self._prev = prev
        self._args = args

    def As(self, alias: Name | str) -> TableFunctionRefAliased:
        if isinstance(alias, str):
            alias = Name(alias)
        return TableFunctionRefAliased(self, alias)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append("(")
        comma_separated(buffer, self._args)
        buffer.append(")")


class TableFunctionRef(SqlElement):
    """Table function name — call it to produce a table-function-ref."""

    def __init__(self, name: Name | str, schema: Name | str | None = None) -> None:
        if isinstance(name, str):
            name = Name(name)
        if isinstance(schema, str):
            schema = Name(schema)
        self._name = name
        self._schema = schema

    def __call__(self, *args: SqlElement) -> TableFunctionRefCall:
        return TableFunctionRefCall(self, args)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        if self._schema is not None:
            self._schema._create_query(buffer)
            buffer.append(".")
        self._name._create_query(buffer)


class SubqueryAliased(TableOrSubquery):
    def __init__(self, prev: SqlElement, alias: Name) -> None:
        self._prev = prev
        self._alias = alias

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" AS ")
        self._alias._create_query(buffer)


class Subquery(TableOrSubquery):
    """A SELECT statement wrapped in parentheses as a table source."""

    def __init__(self, select_stmt: SelectStatement) -> None:
        self._select_stmt = select_stmt

    def As(self, alias: Name | str) -> SubqueryAliased:
        if isinstance(alias, str):
            alias = Name(alias)
        return SubqueryAliased(self, alias)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("(")
        self._select_stmt._create_query(buffer)
        buffer.append(")")


class NestedFromClause(TableOrSubquery):
    """(table-or-subquery, ... | join-clause) — nested FROM clause."""

    def __init__(self, sources: tuple[TableOrSubquery, ...] | JoinClause) -> None:
        self._sources = sources

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("(")
        if isinstance(self._sources, JoinClause):
            self._sources._create_query(buffer)
        else:
            comma_separated(buffer, self._sources)
        buffer.append(")")


class JoinRhsNoConstraint(SqlElement):
    """Internal: join-op + rhs for NATURAL joins (no constraint needed)."""

    def __init__(
        self, lhs: TableOrSubquery, keyword: str, rhs: TableOrSubquery
    ) -> None:
        self._lhs = lhs
        self._keyword = keyword
        self._rhs = rhs

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._lhs._create_query(buffer)
        buffer.append(self._keyword)
        buffer.append(" ")
        self._rhs._create_query(buffer)


class JoinClause(TableOrSubquery):
    """A complete join clause — can be extended with more joins."""

    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)


class JoinOn(SqlElement):
    """join-op + rhs + ON expr — intermediate, pending constraint."""

    def __init__(self, prev: SqlElement, expr: SqlElement) -> None:
        self._prev = prev
        self._expr = expr

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ON ")
        self._expr._create_query(buffer)


class JoinUsing(SqlElement):
    """join-op + rhs + USING (cols) — intermediate, pending constraint."""

    def __init__(self, prev: SqlElement, cols: tuple[Name, ...]) -> None:
        self._prev = prev
        self._cols = cols

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" USING (")
        comma_separated(buffer, self._cols)
        buffer.append(")")


class JoinRhs(SqlElement):
    """Intermediate: lhs + join-op + rhs, awaiting ON/USING constraint."""

    def __init__(
        self, lhs: TableOrSubquery, keyword: str, rhs: TableOrSubquery
    ) -> None:
        self._lhs = lhs
        self._keyword = keyword
        self._rhs = rhs

    def On(self, expr: SqlElement) -> JoinClause:
        return JoinClause(JoinOn(self, expr))

    def Using(self, *cols: Name | str) -> JoinClause:
        names = tuple(Name(c) if isinstance(c, str) else c for c in cols)
        return JoinClause(JoinUsing(self, names))

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._lhs._create_query(buffer)
        buffer.append(self._keyword)
        buffer.append(" ")
        self._rhs._create_query(buffer)
