from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from sqlinpython.base import CompleteSqlQuery
from sqlinpython.name import Name

if TYPE_CHECKING:
    from sqlinpython.table_or_subquery import SubqueryAliased


class Complete:
    pass


class Core(Complete):
    pass


class SelectStatement_[T: Core | Complete](CompleteSqlQuery, ABC):
    """Abstract base for SELECT statements. Isolated to avoid circular imports."""

    def As(self, alias: Name | str) -> SubqueryAliased:
        from sqlinpython.table_or_subquery import SubqueryAliased as SubqueryAliased_

        if isinstance(alias, str):
            alias = Name(alias)
        return SubqueryAliased_(self, alias)


SelectStatement = SelectStatement_[Complete]
