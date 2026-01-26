from __future__ import annotations

from typing import overload

from sqlinpython.base import SqlElement
from sqlinpython.conflict_clause import OnConflict_, OnConflictAction
from sqlinpython.expression import Expression
from sqlinpython.indexed_column import IndexedColumn
from sqlinpython.name import Name


class ConstraintKeyword(SqlElement):
    def __call__(self, name: Name | str) -> ConstraintWithName:
        if isinstance(name, str):
            name = Name(name)
        return ConstraintWithName(self, name)

    def _create_query(self):
        return "CONSTRAINT"


Constraint = ConstraintKeyword()


class ConstraintWithName(SqlElement):
    def __init__(self, prev: SqlElement, name: Name) -> None:
        self._prev = prev
        self._name = name

    @property
    def PrimaryKey(self) -> PrimaryKeyConstraint:
        return PrimaryKeyConstraint(self)

    @property
    def Unique(self) -> UniqueConstraint:
        return UniqueConstraint(self)

    def Check(self, expr: Expression) -> CheckConstraint:
        return CheckConstraint(self, expr)

    # TODO
    # @property
    # def ForeignKey(self) -> ForeignKeyConstraint:
    #     return ForeignKeyConstraint(self)

    def _create_query(self):
        return f"{self._prev._create_query()} {self._name._create_query()}"


class PrimaryKeyConstraint(SqlElement):
    def __init__(self, prev: ConstraintWithName | None) -> None:
        self._prev = prev

    @overload
    def __call__(
        self, column: IndexedColumn, /, *, autoincrement: bool = False
    ) -> ConstraintBeforeConflictClause: ...

    @overload
    def __call__(self, *columns: IndexedColumn) -> ConstraintBeforeConflictClause: ...
    def __call__(
        self, *columns: IndexedColumn, autoincrement: bool = False
    ) -> ConstraintBeforeConflictClause:
        return ConstraintBeforeConflictClause(self, columns, autoincrement)

    def _create_query(self):
        if self._prev is None:
            return "PRIMARY KEY"
        else:
            return f"{self._prev._create_query()} PRIMARY KEY"


PrimaryKey = PrimaryKeyConstraint(None)


class UniqueConstraint(SqlElement):
    def __init__(self, prev: ConstraintWithName | None) -> None:
        self._prev = prev

    def __call__(self, *columns: IndexedColumn) -> ConstraintBeforeConflictClause:
        return ConstraintBeforeConflictClause(self, columns)

    def _create_query(self):
        if self._prev is None:
            return "UNIQUE"
        else:
            return f"{self._prev._create_query()} UNIQUE"


Unique = UniqueConstraint(None)


class TableConstraint(SqlElement):
    pass


class TableConstraintWithConflictClause(OnConflictAction, TableConstraint):
    pass


class ConstraintBeforeConflictClause(TableConstraintWithConflictClause):
    def __init__(
        self,
        prev: SqlElement,
        columns: tuple[IndexedColumn, ...],
        autoincrement: bool = False,
    ) -> None:
        self._prev = prev
        self._columns = columns
        self._autoincrement = autoincrement

    def OnConflict(self) -> OnConflict_[TableConstraintWithConflictClause]:
        return OnConflict_(TableConstraintWithConflictClause, self)

    def _create_query(self):
        columns = ", ".join(column._create_query() for column in self._columns)
        autoincrement = " AUTOINCREMENT" if self._autoincrement else ""
        return f"{self._prev._create_query()} ({columns}{autoincrement})"


class CheckConstraint(TableConstraint):
    def __init__(self, prev: ConstraintWithName | None, expr: Expression) -> None:
        self._prev = prev
        self._expr = expr

    def _create_query(self):
        if self._prev is None:
            return f"CHECK ({self._expr._create_query()})"
        else:
            return f"{self._prev._create_query()} CHECK ({self._expr._create_query()})"


def Check(expr: Expression) -> CheckConstraint:
    return CheckConstraint(None, expr)
