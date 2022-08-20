from __future__ import annotations

from typing import Literal

import sqlinpython.create_table
import sqlinpython.expression
import sqlinpython.select_expression
from sqlinpython.base import CompleteSqlQuery, NotImplementedSqlElement, SqlElement
from sqlinpython.name import Name
from sqlinpython.reference import SqlRef

from .column_def import ColumnDef


class Hint(NotImplementedSqlElement):
    pass


class TableSpecWithJoin(SqlElement):
    def Join(
        self, other: TableSpec, on: sqlinpython.expression.Expression
    ) -> TableSpecWithJoin:
        return TableSpecWithJoin(self, other, "", on)

    def InnerJoin(
        self, other: TableSpec, on: sqlinpython.expression.Expression
    ) -> TableSpecWithJoin:
        return TableSpecWithJoin(self, other, "INNER", on)

    def LeftJoin(
        self, other: TableSpec, on: sqlinpython.expression.Expression
    ) -> TableSpecWithJoin:
        return TableSpecWithJoin(self, other, "LEFT", on)

    def LeftOuterJoin(
        self, other: TableSpec, on: sqlinpython.expression.Expression
    ) -> TableSpecWithJoin:
        return TableSpecWithJoin(self, other, "LEFT OUTER", on)

    def RightJoin(
        self, other: TableSpec, on: sqlinpython.expression.Expression
    ) -> TableSpecWithJoin:
        return TableSpecWithJoin(self, other, "RIGHT", on)

    def RightOuterJoin(
        self, other: TableSpec, on: sqlinpython.expression.Expression
    ) -> TableSpecWithJoin:
        return TableSpecWithJoin(self, other, "RIGHT OUTER", on)

    def __init__(
        self,
        prev: SqlElement,
        with_: TableSpecWithJoin,
        how: Literal["", "INNER", "LEFT", "LEFT OUTER", "RIGHT", "RIGHT OUTER"],
        on: sqlinpython.expression.Expression,
    ) -> None:
        self._prev = prev
        self._with = with_
        self._how = how
        self._on = on

    def _create_query(self) -> str:
        join = self._how + " JOIN" if self._how else "JOIN"
        return (
            f"{self._prev._create_query()} {join} {self._with._create_query()}"
            f" ON {self._on._create_query()}"
        )


class TableSpec(TableSpecWithJoin):
    pass


class AliasedTableRef(TableSpec):
    pass


class TableRefWithTableSample(AliasedTableRef):
    def __init__(self, prev: SqlElement, fraction: float):
        self._prev = prev
        self._fraction = fraction

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} TABLESAMPLE({self._fraction})"


class TableRefWithColumnDef(TableRefWithTableSample):
    def __init__(self, prev: SqlElement, column_defs: tuple[ColumnDef, ...]) -> None:
        self._prev = prev
        self._column_defs = column_defs

    def _create_query(self) -> str:
        column_defs = ", ".join(col._create_query() for col in self._column_defs)
        return f"{self._prev._create_query()}({column_defs})"

    def TableSample(self, fraction: float) -> TableRefWithTableSample:
        return TableRefWithTableSample(self, fraction)


class TableRefWithAlias(TableRefWithColumnDef):
    def __init__(self, prev: SqlElement, alias: Name, explicit_as: bool):
        self._prev = prev
        self._alias = alias
        self._explicit_as = explicit_as

    def _create_query(self) -> str:
        as_ = ""
        if self._explicit_as:
            as_ = "AS "
        return f"{self._prev._create_query()} {as_}{self._alias._create_query()}"

    def __call__(self, *column_defs: ColumnDef) -> TableRefWithColumnDef:
        return TableRefWithColumnDef(self, column_defs)


class TableRef(SqlRef, TableRefWithAlias):
    def As(self, alias: Name | str, explicit_as: bool = True) -> TableRefWithAlias:
        if isinstance(alias, str):
            alias = Name(alias)

        return TableRefWithAlias(self, alias, explicit_as)


class SelectStatementWithDistinctOrAll(SqlElement):
    def __init__(self, prev: SqlElement, kind: Literal["DISTINCT", "ALL"]):
        self._prev = prev
        self._kind = kind

    def __call__(
        self,
        first_select_expression: sqlinpython.select_expression.SelectExpression,
        /,
        *other_select_expressions: sqlinpython.select_expression.SelectExpression,
    ) -> SelectStatementWithSelectExpression:
        """
        TODO: Explain All
        """
        select_expressions = (first_select_expression, *other_select_expressions)
        return SelectStatementWithSelectExpression(self, select_expressions)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._kind}"


class SelectStatementWithHint(SelectStatementWithDistinctOrAll):
    def __init__(self, prev: SqlElement, hint: Hint):
        self._prev = prev
        self._hint = hint

    @property
    def Distinct(
        self,
    ) -> SelectStatementWithDistinctOrAll:
        return SelectStatementWithDistinctOrAll(self, "DISTINCT")

    @property
    def All(
        self,
    ) -> SelectStatementWithDistinctOrAll:
        return SelectStatementWithDistinctOrAll(self, "ALL")

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} /*{self._hint._create_query()}*/"


class SelectKeyword(SelectStatementWithHint):
    def __init__(self) -> None:
        pass

    def hint(self, hint: Hint) -> SelectStatementWithHint:
        return SelectStatementWithHint(self, hint)

    def _create_query(self) -> str:
        return f"SELECT"


class SelectStatementWithSelectExpression(SqlElement):
    def __init__(
        self,
        prev: SqlElement,
        select_expressions: tuple[sqlinpython.select_expression.SelectExpression, ...],
    ) -> None:
        self._prev = prev
        self._select_expressions = select_expressions

    def From(self, table_spec: TableSpecWithJoin) -> SelectStatementWithFrom:
        return SelectStatementWithFrom(self, table_spec)

    def _create_query(self) -> str:
        select_query = ", ".join(
            expression._create_query() for expression in self._select_expressions
        )
        return f"{self._prev._create_query()} {select_query}"


class SelectWithAlias(TableSpec):
    def __init__(self, prev: SqlElement, alias: Name, explicit_as: bool):
        self._prev = prev
        self._alias = alias
        self._explicit_as = explicit_as

    def _create_query(self) -> str:
        as_ = ""
        if self._explicit_as:
            as_ = "AS "
        return f"{self._prev._create_query()} {as_}{self._alias._create_query()}"


class SelectType(CompleteSqlQuery):
    def As(self, alias: Name | str, explicit_as: bool = True) -> SelectWithAlias:
        if isinstance(alias, str):
            alias = Name(alias)

        return SelectWithAlias(self.Parenticies, alias, explicit_as)

    @property
    def Parenticies(self) -> SelectWithParenticies:
        return SelectWithParenticies(self)


class SelectWithParenticies(TableSpec):
    def __init__(self, select: SelectType) -> None:
        self._select = select

    def _create_query(self) -> str:
        return f"({self._select._create_query()})"


class SelectWithFetchComplete(SelectType):
    def __init__(
        self, prev: SqlElement, row_only: Literal["ROW ONLY", "ROWS ONLY"]
    ) -> None:
        self._prev = prev
        self._row_only = row_only

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._row_only}"


class SelectWithFetchCount(SqlElement):
    def __init__(
        self,
        prev: SelectWithFetch,
        operation: Literal["NEXT", "FIRST"],
        param: int | sqlinpython.create_table.BindParameter,
    ) -> None:
        self._prev = prev
        self._operation = operation
        self._param = (
            sqlinpython.expression.Value(param) if isinstance(param, int) else param
        )

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._operation} {self._param._create_query()}"

    @property
    def RowOnly(self) -> SelectWithFetchComplete:
        return SelectWithFetchComplete(self, "ROW ONLY")

    @property
    def RowsOnly(self) -> SelectWithFetchComplete:
        return SelectWithFetchComplete(self, "ROWS ONLY")


class SelectWithFetch(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} FETCH"

    def Next(
        self, param: int | sqlinpython.create_table.BindParameter
    ) -> SelectWithFetchCount:
        return SelectWithFetchCount(self, "NEXT", param)

    def First(
        self, param: int | sqlinpython.create_table.BindParameter
    ) -> SelectWithFetchCount:
        return SelectWithFetchCount(self, "FIRST", param)


class SelectWithOffsetComplete(SelectWithFetchComplete):
    def __init__(self, prev: SqlElement, row: Literal["ROW", "ROWS"]) -> None:
        self._prev = prev
        self._row = row

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._row}"

    @property
    def Fetch(self) -> SelectWithFetch:
        return SelectWithFetch(self)


class SelectWithOffset(SelectWithOffsetComplete):
    def __init__(
        self, prev: SqlElement, param: int | sqlinpython.create_table.BindParameter
    ) -> None:
        self._prev = prev
        self._param = (
            sqlinpython.expression.Value(param) if isinstance(param, int) else param
        )

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} OFFSET {self._param._create_query()}"

    @property
    def Row(self) -> SelectWithOffsetComplete:
        return SelectWithOffsetComplete(self, "ROW")

    @property
    def Rows(self) -> SelectWithOffsetComplete:
        return SelectWithOffsetComplete(self, "ROWS")


class SelectWithLimit(SelectWithOffsetComplete):
    def __init__(
        self, prev: SqlElement, param: int | sqlinpython.create_table.BindParameter
    ) -> None:
        self._prev = prev
        self._param = (
            sqlinpython.expression.Value(param) if isinstance(param, int) else param
        )

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} LIMIT {self._param._create_query()}"

    def Offset(
        self, param: int | sqlinpython.create_table.BindParameter
    ) -> SelectWithOffset:
        return SelectWithOffset(self, param)


class SelectWithOrderBy(SelectWithLimit):
    def __init__(
        self, prev: SqlElement, orders: tuple[sqlinpython.expression.Order, ...]
    ) -> None:
        self._prev = prev
        self._orders = orders

    def _create_query(self) -> str:
        orders = ", ".join(order._create_query() for order in self._orders)
        return f"{self._prev._create_query()} ORDER BY {orders}"

    def Limit(
        self, param: int | sqlinpython.create_table.BindParameter
    ) -> SelectWithLimit:
        return SelectWithLimit(self, param)


class SelectWithUnionAll(SelectWithOrderBy):
    def __init__(self, prev: SqlElement, select_statement: SelectStatement) -> None:
        self._prev = prev
        self._select_statement = select_statement

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} UNION ALL {self._select_statement._create_query()}"

    def UnionAll(self, select_statement: SelectStatement) -> SelectWithUnionAll:
        return SelectWithUnionAll(self, select_statement)

    def OrderBy(
        self,
        first_order: sqlinpython.expression.Order,
        *other_orders: sqlinpython.expression.Order,
    ) -> SelectWithOrderBy:
        orders = (first_order, *other_orders)
        return SelectWithOrderBy(self, orders)


class SelectStatement(SelectWithUnionAll):
    pass


class SelectStatementWithHaving(SelectStatement):
    def __init__(
        self, prev: SqlElement, expression: sqlinpython.expression.Expression
    ) -> None:
        self._prev = prev
        self._expression = expression

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} HAVING {self._expression._create_query()}"


class SelectStatementWithGroupBy(SelectStatementWithHaving):
    def __init__(
        self,
        prev: SqlElement,
        expressions: tuple[sqlinpython.expression.Expression, ...],
    ) -> None:
        self._prev = prev
        self._expressions = expressions

    def Having(
        self,
        expression: sqlinpython.expression.Expression,
    ) -> SelectStatementWithHaving:
        return SelectStatementWithHaving(self, expression)

    def _create_query(self) -> str:
        groupby = ", ".join(
            expression._create_query() for expression in self._expressions
        )
        return f"{self._prev._create_query()} GROUP BY {groupby}"


class SelectStatementWithWhere(SelectStatementWithGroupBy):
    def __init__(
        self, prev: SqlElement, expression: sqlinpython.expression.Expression
    ) -> None:
        self._prev = prev
        self._expression = expression

    def GroupBy(
        self,
        first_expression: sqlinpython.expression.Expression,
        /,
        *other_expressions: sqlinpython.expression.Expression,
    ) -> SelectStatementWithGroupBy:
        expressions = (first_expression, *other_expressions)
        return SelectStatementWithGroupBy(self, expressions)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} WHERE {self._expression._create_query()}"


class SelectStatementWithFrom(SelectStatementWithWhere):
    def __init__(self, prev: SqlElement, table_spec: TableSpecWithJoin) -> None:
        self._prev = prev
        self._table_spec = table_spec

    def Where(
        self, expression: sqlinpython.expression.Expression
    ) -> SelectStatementWithWhere:
        return SelectStatementWithWhere(self, expression)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} FROM {self._table_spec._create_query()}"


Select = SelectKeyword()
