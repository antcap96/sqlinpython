from __future__ import annotations

from typing import Literal

from sqlinpython.base import NotImplementedSqlElement, SqlElement, CompleteSqlQuery
from sqlinpython.expression import Expression, Order, Value
from sqlinpython.select_expression import SelectExpression
from sqlinpython.create_table import BindParameter


class Hint(NotImplementedSqlElement):
    pass


class SelectStatementWithDistinctOrAll(SqlElement):
    def __init__(self, prev: SqlElement, kind: Literal["DISTINCT", "ALL"]):
        self._prev = prev
        self._kind = kind

    def __call__(
        self,
        first_select_expression: SelectExpression,
        /,
        *other_select_expressions: SelectExpression,
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
        self, prev: SqlElement, select_expressions: tuple[SelectExpression, ...]
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


class SelectType(CompleteSqlQuery):
    pass


class SelectWithFetchComplete(SelectType):
    def __init__(
        self, prev: SqlElement, row_only: Literal["ROW ONLY", "ROWS ONLY"]
    ) -> None:
        self._prev = prev
        self._row_only = row_only

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._row_only}"


class SelectWithFetchCount(SqlElement):
    def __init__(self, prev: SelectWithFetch, param: int | BindParameter) -> None:
        self._prev = prev
        self._param = param if isinstance(param, BindParameter) else Value(param)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._param._create_query()}"

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

    def Next(self, param: int | BindParameter) -> SelectWithFetchCount:
        pass

    def First(self, param: int | BindParameter) -> SelectWithFetchCount:
        pass


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
    def __init__(self, prev: SqlElement, param: int | BindParameter) -> None:
        self._prev = prev
        self._param = param if isinstance(param, BindParameter) else Value(param)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} OFFSET {self._param._create_query()}"

    @property
    def Row(self) -> SelectWithOffsetComplete:
        return SelectWithOffsetComplete(self, "ROW")

    @property
    def Rows(self) -> SelectWithOffsetComplete:
        return SelectWithOffsetComplete(self, "ROWS")


class SelectWithLimit(SelectWithOffsetComplete):
    def __init__(self, prev: SqlElement, param: int | BindParameter) -> None:
        self._prev = prev
        self._param = param if isinstance(param, BindParameter) else Value(param)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} LIMIT {self._param._create_query()}"

    def Offset(self, param: int | BindParameter) -> SelectWithOffset:
        return SelectWithOffset(self, param)


class SelectWithOrderBy(SelectWithLimit):
    def __init__(self, prev: SqlElement, orders: tuple[Order, ...]) -> None:
        self._prev = prev
        self._orders = orders

    def _create_query(self) -> str:
        orders = ", ".join(order._create_query() for order in self._orders)
        return f"{self._prev._create_query()} ORDER BY {orders}"

    def Limit(self, param: int | BindParameter) -> SelectWithLimit:
        return SelectWithLimit(self, param)


class SelectWithUnionAll(SelectWithOrderBy):
    def __init__(self, prev: SqlElement, select_statement: SelectStatement) -> None:
        self._prev = prev
        self._select_statement = select_statement

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} UNION ALL {self._select_statement._create_query()}"

    def UnionAll(self, select_statement: SelectStatement) -> SelectWithUnionAll:
        return SelectWithUnionAll(self, select_statement)

    def OrderBy(self, first_order: Order, *other_orders: Order) -> SelectWithOrderBy:
        orders = (first_order, *other_orders)
        return SelectWithOrderBy(self, orders)


class SelectStatement(SelectWithUnionAll):
    pass


class SelectStatementWithHaving(SelectStatement):
    def __init__(self, prev: SqlElement, expression: Expression) -> None:
        self._prev = prev
        self._expression = expression

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} HAVING {self._expression._create_query()}"


class SelectStatementWithGroupBy(SelectStatementWithHaving):
    def __init__(self, prev: SqlElement, expressions: tuple[Expression, ...]) -> None:
        self._prev = prev
        self._expressions = expressions

    def Having(
        self,
        expression: Expression,
    ) -> SelectStatementWithHaving:
        return SelectStatementWithHaving(self, expression)

    def _create_query(self) -> str:
        groupby = ", ".join(
            expression._create_query() for expression in self._expressions
        )
        return f"{self._prev._create_query()} GROUP BY {groupby}"


class SelectStatementWithWhere(SelectStatementWithGroupBy):
    def __init__(self, prev: SqlElement, expression: Expression) -> None:
        self._prev = prev
        self._expression = expression

    def GroupBy(
        self,
        first_expression: Expression,
        /,
        *other_expressions: Expression,
    ) -> SelectStatementWithGroupBy:
        expressions = (first_expression, *other_expressions)
        return SelectStatementWithGroupBy(self, expressions)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} WHERE {self._expression._create_query()}"


class SelectStatementWithFrom(SelectStatementWithWhere):
    def __init__(self, prev: SqlElement, table_spec: TableSpecWithJoin) -> None:
        self._prev = prev
        self._table_spec = table_spec

    def Where(self, expression: Expression) -> SelectStatementWithWhere:
        return SelectStatementWithWhere(self, expression)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} FROM {self._table_spec._create_query()}"


class TableSpecWithJoin(SqlElement):
    def Join(self, other: TableSpec, on: Expression) -> TableSpecWithJoin:
        return TableSpecWithJoin(self, other, "", on)

    def InnerJoin(self, other: TableSpec, on: Expression) -> TableSpecWithJoin:
        return TableSpecWithJoin(self, other, "INNER", on)

    def LeftJoin(self, other: TableSpec, on: Expression) -> TableSpecWithJoin:
        return TableSpecWithJoin(self, other, "LEFT", on)

    def LeftOuterJoin(self, other: TableSpec, on: Expression) -> TableSpecWithJoin:
        return TableSpecWithJoin(self, other, "LEFT OUTER", on)

    def RightJoin(self, other: TableSpec, on: Expression) -> TableSpecWithJoin:
        return TableSpecWithJoin(self, other, "RIGHT", on)

    def RightOuterJoin(self, other: TableSpec, on: Expression) -> TableSpecWithJoin:
        return TableSpecWithJoin(self, other, "RIGHT OUTER", on)

    def __init__(
        self,
        prev: TableSpecWithJoin,
        with_: TableSpecWithJoin,
        how: Literal["", "INNER", "LEFT", "LEFT OUTER", "RIGHT", "RIGHT OUTER"],
        on: Expression,
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


class TableSpec(NotImplementedSqlElement, TableSpecWithJoin):
    pass


Select = SelectKeyword()
