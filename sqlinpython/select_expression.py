from __future__ import annotations

from abc import ABCMeta

from sqlinpython.base import SqlElement
from sqlinpython.name import Name


class SelectExpression(SqlElement, metaclass=ABCMeta):
    pass


class SelectExpressionWithAlias(SelectExpression):
    def __init__(self, prev: SqlElement, alias: Name, explicit_as: bool) -> None:
        self._prev = prev
        self._alias = alias
        self._explicit_as = explicit_as

    def _create_query(self) -> str:
        as_ = ""
        if self._explicit_as:
            as_ = "AS "
        return f"{self._prev._create_query()} {as_}{self._alias._create_query()}"


class StarKeyword(SelectExpression):
    def __call__(self, family: Name | str) -> FamilyNameStar:
        if isinstance(family, str):
            family = Name(family)
        return FamilyNameStar(family)

    def _create_query(self) -> str:
        return "*"


class FamilyNameStar(SelectExpression):
    def __init__(self, family: Name):
        self._family = family

    def _create_query(self) -> str:
        return f"{self._family._create_query()}.*"


# TODO: This name might not be the best
Star = StarKeyword()
