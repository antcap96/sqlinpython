from __future__ import annotations

from abc import ABCMeta
from typing import Literal

from sqlinpython.base import CompleteSqlQuery, NotImplementedSqlElement, SqlElement
from sqlinpython.create_table import BindParameter
from sqlinpython.expression import Expression, Value
from sqlinpython.name import Name
from sqlinpython.order import Order
from sqlinpython.select_expression import SelectExpression
from sqlinpython.table_spec import TableSpec, TableSpecWithJoin


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
        TODO: Explain Star
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

    def Hint(self, hint: Hint) -> SelectStatementWithHint:
        return SelectStatementWithHint(self, hint)

    def _create_query(self) -> str:
        return f"SELECT"


class SelectStatementWithSelectExpression(SqlElement):
    def __init__(
        self,
        prev: SqlElement,
        select_expressions: tuple[SelectExpression, ...],
    ) -> None:
        self._prev = prev
        self._select_expressions = select_expressions

    def From(
        self, table_spec: TableSpecWithJoin | SelectType
    ) -> SelectStatementWithFrom:
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


class SelectType(CompleteSqlQuery, metaclass=ABCMeta):
    def As(self, alias: Name | str, explicit_as: bool = True) -> SelectWithAlias:
        if isinstance(alias, str):
            alias = Name(alias)

        return SelectWithAlias(self._parentheses, alias, explicit_as)

    @property
    def _parentheses(self) -> SelectWithParentheses:
        return SelectWithParentheses(self)


class SelectWithParentheses(TableSpec):
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
        param: int | BindParameter,
    ) -> None:
        self._prev = prev
        self._operation = operation
        self._param = Value(param) if isinstance(param, int) else param

    def _create_query(self) -> str:
        op = self._operation
        return f"{self._prev._create_query()} {op} {self._param._create_query()}"

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
        return SelectWithFetchCount(self, "NEXT", param)

    def First(self, param: int | BindParameter) -> SelectWithFetchCount:
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
    def __init__(self, prev: SqlElement, param: int | BindParameter) -> None:
        self._prev = prev
        self._param = Value(param) if isinstance(param, int) else param

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
        self._param = Value(param) if isinstance(param, int) else param

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
        return (
            f"{self._prev._create_query()} UNION ALL"
            f" {self._select_statement._create_query()}"
        )

    def UnionAll(self, select_statement: SelectStatement) -> SelectWithUnionAll:
        return SelectWithUnionAll(self, select_statement)

    def OrderBy(
        self,
        first_order: Order,
        *other_orders: Order,
    ) -> SelectWithOrderBy:
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
    def __init__(
        self,
        prev: SqlElement,
        expressions: tuple[Expression, ...],
    ) -> None:
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
    def __init__(
        self, prev: SqlElement, table_spec: TableSpecWithJoin | SelectType
    ) -> None:
        self._prev = prev
        self._table_spec: TableSpecWithJoin
        if isinstance(table_spec, SelectType):
            self._table_spec = table_spec._parentheses
        else:
            self._table_spec = table_spec

    def Where(self, expression: Expression) -> SelectStatementWithWhere:
        return SelectStatementWithWhere(self, expression)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} FROM {self._table_spec._create_query()}"


Select = SelectKeyword()
