from __future__ import annotations

import typing
from typing import override

from sqlinpython.column_definition import (
    ColumnNameWithType,
    GeneratedAlwaysAs,
    WithCollate,
)
from sqlinpython.expression.core import (
    AliasedExpression,
    CollateOperator,
    Expression,
    Expression12,
)
from sqlinpython.name import Name
from sqlinpython.type_name import CompleteTypeName


# Both indexed-column (https://sqlite.org/syntax/indexed-column.html) and
# column-def (https://sqlite.org/syntax/column-def.html + https://sqlite.org/syntax/column-constraint.html)
# allow ColumnName.Collate
class ColumnNameWithCollate(CollateOperator, WithCollate):
    @override
    def Collate(self, collation_name: str | Name, /) -> ColumnNameWithCollate:
        if isinstance(collation_name, str):
            collation_name = Name(collation_name)
        return ColumnNameWithCollate(self, collation_name)

    # Override to handle both contexts:
    # - Expression context: col.Collate("NOCASE").As("alias") -> AliasedExpression
    # - Column definition context: col.Collate("utf8").As(expr) -> GeneratedAlwaysAs
    @typing.overload
    def As(self, alias: str | Name, /) -> AliasedExpression: ...

    @typing.overload
    def As(self, expression: Expression, /) -> GeneratedAlwaysAs: ...

    @override
    def As(
        self, alias_or_expr: str | Name | Expression, /
    ) -> AliasedExpression | GeneratedAlwaysAs:
        if isinstance(alias_or_expr, (str, Name)):
            if isinstance(alias_or_expr, str):
                alias_or_expr = Name(alias_or_expr)
            return AliasedExpression(self, alias_or_expr)
        return GeneratedAlwaysAs(self, alias_or_expr)


# TODO: Any better way to handle mypy error "incompatible with definition in base class"
class ColumnName(Name, ColumnNameWithType, Expression12):  # type: ignore [misc]
    def __call__(self, type_name: CompleteTypeName) -> ColumnNameWithType:
        return ColumnNameWithType(self, type_name)

    @override
    def Collate(self, collation_name: str | Name, /) -> ColumnNameWithCollate:
        if isinstance(collation_name, str):
            collation_name = Name(collation_name)
        return ColumnNameWithCollate(self, collation_name)

    @typing.overload
    def As(self, alias: str | Name, /) -> AliasedExpression: ...

    @typing.overload
    def As(self, expression: Expression, /) -> GeneratedAlwaysAs: ...

    @override
    def As(
        self, alias_or_expr: str | Name | Expression, /
    ) -> AliasedExpression | GeneratedAlwaysAs:
        if isinstance(alias_or_expr, (str, Name)):
            if isinstance(alias_or_expr, str):
                alias_or_expr = Name(alias_or_expr)
            return AliasedExpression(self, alias_or_expr)
        return GeneratedAlwaysAs(self, alias_or_expr)
