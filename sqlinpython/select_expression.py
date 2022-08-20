from __future__ import annotations
from sqlinpython.name import Name
from sqlinpython.base import SqlElement
from sqlinpython.expression import Expression


class SelectExpression(SqlElement):
    pass


class Alias(SelectExpression):
    def __init__(self, expression: Expression) -> None:
        self._expression = expression

    def As(self, alias: Name | str, show_as: bool = True) -> SelectExpressionWithAlias:
        if isinstance(alias, str):
            alias = Name(alias)

        return SelectExpressionWithAlias(self, alias, show_as)

    def _create_query(self) -> str:
        return self._expression._create_query()


class SelectExpressionWithAlias(SelectExpression):
    def __init__(self, prev: Alias, alias: Name, show_as: bool) -> None:
        self._prev = prev
        self._alias = alias
        self._show_as = show_as

    def _create_query(self) -> str:
        as_ = ""
        if self._show_as:
            as_ = "AS "
        return f"{self._prev._create_query()} {as_}{self._alias._create_query()}"


class AllKeyword(SelectExpression):
    def __call__(self, family: Name | str) -> FamilyNameAll:
        if isinstance(family, str):
            family = Name(family)
        return FamilyNameAll(family)

    def _create_query(self) -> str:
        return "*"


class FamilyNameAll(SelectExpression):
    def __init__(self, family: Name):
        self._family = family

    def _create_query(self) -> str:
        return f"{self._family._create_query()}.*"


All = AllKeyword()
