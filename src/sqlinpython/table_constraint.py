from __future__ import annotations

from typing import TYPE_CHECKING, overload

from sqlinpython.base import SqlElement
from sqlinpython.conflict_clause import OnConflict_, OnConflictAction
from sqlinpython.expression import Expression
from sqlinpython.indexed_column import IndexedColumn
from sqlinpython.name import Name

if TYPE_CHECKING:
    from sqlinpython.foreign_key_clause import References_


class ConstraintKeyword(SqlElement):
    def __call__(self, name: Name | str) -> ConstraintWithName:
        if isinstance(name, str):
            name = Name(name)
        return ConstraintWithName(self, name)

    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("CONSTRAINT")


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

    def ForeignKey(self, *column_names: str | Name) -> ForeignKeyConstraint:
        names = tuple(
            column_name if isinstance(column_name, Name) else Name(column_name)
            for column_name in column_names
        )
        return ForeignKeyConstraint(self, names)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._name._create_query(buffer)


class ForeignKeyConstraint(SqlElement):
    def __init__(
        self, prev: ConstraintWithName | None, column_names: tuple[Name, ...]
    ) -> None:
        self._prev = prev
        self._column_names = column_names

    def References(self, foreign_table_name: Name | str) -> References_:
        from sqlinpython.foreign_key_clause import References_

        if isinstance(foreign_table_name, str):
            foreign_table_name = Name(foreign_table_name)

        return References_(self, foreign_table_name)

    def _create_query(self, buffer: list[str]) -> None:
        if self._prev is not None:
            self._prev._create_query(buffer)
            buffer.append(" FOREIGN KEY(")
        else:
            buffer.append("FOREIGN KEY(")
        for i, column_name in enumerate(self._column_names):
            if i > 0:
                buffer.append(", ")
            column_name._create_query(buffer)
        buffer.append(")")


def ForeignKey(*column_names: Name | str) -> ForeignKeyConstraint:
    names = tuple(
        Name(column_name) if isinstance(column_name, str) else column_name
        for column_name in column_names
    )
    return ForeignKeyConstraint(None, names)


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

    def _create_query(self, buffer: list[str]) -> None:
        if self._prev is None:
            buffer.append("PRIMARY KEY")
        else:
            self._prev._create_query(buffer)
            buffer.append(" PRIMARY KEY")


PrimaryKey = PrimaryKeyConstraint(None)


class UniqueConstraint(SqlElement):
    def __init__(self, prev: ConstraintWithName | None) -> None:
        self._prev = prev

    def __call__(self, *columns: IndexedColumn) -> ConstraintBeforeConflictClause:
        return ConstraintBeforeConflictClause(self, columns)

    def _create_query(self, buffer: list[str]) -> None:
        if self._prev is None:
            buffer.append("UNIQUE")
        else:
            self._prev._create_query(buffer)
            buffer.append(" UNIQUE")


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

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" (")
        for i, column in enumerate(self._columns):
            if i > 0:
                buffer.append(", ")
            column._create_query(buffer)
        if self._autoincrement:
            buffer.append(" AUTOINCREMENT")
        buffer.append(")")


class CheckConstraint(TableConstraint):
    def __init__(self, prev: ConstraintWithName | None, expr: Expression) -> None:
        self._prev = prev
        self._expr = expr

    def _create_query(self, buffer: list[str]) -> None:
        if self._prev is None:
            buffer.append("CHECK (")
            self._expr._create_query(buffer)
            buffer.append(")")
        else:
            self._prev._create_query(buffer)
            buffer.append(" CHECK (")
            self._expr._create_query(buffer)
            buffer.append(")")


def Check(expr: Expression) -> CheckConstraint:
    return CheckConstraint(None, expr)
