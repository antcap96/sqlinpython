from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.column_definition import ColumnDefinition
from sqlinpython.conflict_clause import OnConflict_, OnConflictAction
from sqlinpython.expression import Expression
from sqlinpython.name import Name

# SPEC: https://www.sqlite.org/lang_altertable.html


class AlterTableStatement(CompleteSqlQuery, ABC):
    pass


class AlterTableWithConflict(OnConflictAction, AlterTableStatement):
    pass


# ----- RENAME -----


class AlterTableRenameTo(AlterTableStatement):
    def __init__(self, prev: SqlElement, new_name: Name) -> None:
        self._prev = prev
        self._new_name = new_name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" TO ")
        self._new_name._create_query(buffer)


class IAlterTableRenameColumnTo(SqlElement, ABC):
    def To(self, new_name: Name | str) -> AlterTableRenameTo:
        if isinstance(new_name, str):
            new_name = Name(new_name)
        return AlterTableRenameTo(self, new_name)


class AlterTableRenameColumn(IAlterTableRenameColumnTo):
    """RENAME COLUMN col — explicit COLUMN keyword"""

    def __init__(self, prev: SqlElement, column_name: Name) -> None:
        self._prev = prev
        self._column_name = column_name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" COLUMN ")
        self._column_name._create_query(buffer)


class AlterTableRenameColumnName(IAlterTableRenameColumnTo):
    """RENAME col — shorthand without COLUMN keyword"""

    def __init__(self, prev: SqlElement, column_name: Name) -> None:
        self._prev = prev
        self._column_name = column_name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._column_name._create_query(buffer)


class AlterTableRename(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def __call__(self, column_name: Name | str) -> AlterTableRenameColumnName:
        if isinstance(column_name, str):
            column_name = Name(column_name)
        return AlterTableRenameColumnName(self, column_name)

    def Column(self, column_name: Name | str) -> AlterTableRenameColumn:
        if isinstance(column_name, str):
            column_name = Name(column_name)
        return AlterTableRenameColumn(self, column_name)

    def To(self, new_name: Name | str) -> AlterTableRenameTo:
        if isinstance(new_name, str):
            new_name = Name(new_name)
        return AlterTableRenameTo(self, new_name)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" RENAME")


# ----- ADD -----


class AlterTableAddColumn(AlterTableStatement):
    """ADD COLUMN col_def — explicit COLUMN keyword"""

    def __init__(self, prev: SqlElement, column_def: ColumnDefinition) -> None:
        self._prev = prev
        self._column_def = column_def

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" COLUMN ")
        self._column_def._create_query(buffer)


class AlterTableAddColumnDef(AlterTableStatement):
    """ADD col_def — shorthand without COLUMN keyword"""

    def __init__(self, prev: SqlElement, column_def: ColumnDefinition) -> None:
        self._prev = prev
        self._column_def = column_def

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._column_def._create_query(buffer)


class AlterTableAddCheck(AlterTableStatement):
    def __init__(self, prev: SqlElement, expr: Expression) -> None:
        self._prev = prev
        self._expr = expr

    @property
    def OnConflict(self) -> OnConflict_[AlterTableWithConflict]:
        return OnConflict_(AlterTableWithConflict, self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" CHECK (")
        self._expr._create_query(buffer)
        buffer.append(")")


class AlterTableAddConstraintWithName(SqlElement):
    def __init__(self, prev: SqlElement, name: Name) -> None:
        self._prev = prev
        self._name = name

    def Check(self, expr: Expression) -> AlterTableAddConstraintCheck:
        return AlterTableAddConstraintCheck(self, expr)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" CONSTRAINT ")
        self._name._create_query(buffer)


class AlterTableAddConstraintCheck(AlterTableStatement):
    def __init__(self, prev: AlterTableAddConstraintWithName, expr: Expression) -> None:
        self._prev = prev
        self._expr = expr

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" CHECK (")
        self._expr._create_query(buffer)
        buffer.append(")")


class AlterTableAdd(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def __call__(self, column_def: ColumnDefinition) -> AlterTableAddColumnDef:
        return AlterTableAddColumnDef(self, column_def)

    def Column(self, column_def: ColumnDefinition) -> AlterTableAddColumn:
        return AlterTableAddColumn(self, column_def)

    def Constraint(self, name: Name | str) -> AlterTableAddConstraintWithName:
        if isinstance(name, str):
            name = Name(name)
        return AlterTableAddConstraintWithName(self, name)

    def Check(self, expr: Expression) -> AlterTableAddCheck:
        return AlterTableAddCheck(self, expr)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ADD")


# ----- DROP -----


class AlterTableDropName(AlterTableStatement):
    """DROP col — shorthand without COLUMN keyword"""

    def __init__(self, prev: SqlElement, name: Name) -> None:
        self._prev = prev
        self._name = name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._name._create_query(buffer)


class AlterTableDropColumn(AlterTableStatement):
    def __init__(self, prev: SqlElement, name: Name) -> None:
        self._prev = prev
        self._name = name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" COLUMN ")
        self._name._create_query(buffer)


class AlterTableDropConstraint(AlterTableStatement):
    def __init__(self, prev: SqlElement, name: Name) -> None:
        self._prev = prev
        self._name = name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" CONSTRAINT ")
        self._name._create_query(buffer)


class AlterTableDrop(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def __call__(self, name: Name | str) -> AlterTableDropName:
        if isinstance(name, str):
            name = Name(name)
        return AlterTableDropName(self, name)

    def Column(self, name: Name | str) -> AlterTableDropColumn:
        if isinstance(name, str):
            name = Name(name)
        return AlterTableDropColumn(self, name)

    def Constraint(self, name: Name | str) -> AlterTableDropConstraint:
        if isinstance(name, str):
            name = Name(name)
        return AlterTableDropConstraint(self, name)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" DROP")


# ----- ALTER COLUMN -----


class AlterTableAlterColumnDropNotNull(AlterTableStatement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" DROP NOT NULL")


class AlterTableAlterColumnSetNotNull(AlterTableStatement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def OnConflict(self) -> OnConflict_[AlterTableWithConflict]:
        return OnConflict_(AlterTableWithConflict, self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" SET NOT NULL")


class IAlterTableAlterColumn(SqlElement, ABC):
    @property
    def SetNotNull(self) -> AlterTableAlterColumnSetNotNull:
        return AlterTableAlterColumnSetNotNull(self)

    @property
    def DropNotNull(self) -> AlterTableAlterColumnDropNotNull:
        return AlterTableAlterColumnDropNotNull(self)


class AlterTableAlterColumn(IAlterTableAlterColumn):
    """ALTER col — shorthand without COLUMN keyword"""

    def __init__(self, prev: SqlElement, column_name: Name) -> None:
        self._prev = prev
        self._column_name = column_name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._column_name._create_query(buffer)


class AlterTableAlterColumnExplicit(IAlterTableAlterColumn):
    """ALTER COLUMN col — explicit COLUMN keyword"""

    def __init__(self, prev: SqlElement, column_name: Name) -> None:
        self._prev = prev
        self._column_name = column_name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" COLUMN ")
        self._column_name._create_query(buffer)


class AlterTableAlter(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def __call__(self, column_name: Name | str) -> AlterTableAlterColumn:
        if isinstance(column_name, str):
            column_name = Name(column_name)
        return AlterTableAlterColumn(self, column_name)

    def Column(self, column_name: Name | str) -> AlterTableAlterColumnExplicit:
        if isinstance(column_name, str):
            column_name = Name(column_name)
        return AlterTableAlterColumnExplicit(self, column_name)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ALTER")


# ----- ENTRY POINT -----


class AlterTable(SqlElement):
    def __init__(self, schema: Name | str, table: Name | str | None = None, /) -> None:
        if isinstance(schema, str):
            schema = Name(schema)
        if isinstance(table, str):
            table = Name(table)
        self._schema = schema
        self._table = table

    @property
    def Rename(self) -> AlterTableRename:
        return AlterTableRename(self)

    @property
    def Add(self) -> AlterTableAdd:
        return AlterTableAdd(self)

    @property
    def Drop(self) -> AlterTableDrop:
        return AlterTableDrop(self)

    @property
    def Alter(self) -> AlterTableAlter:
        return AlterTableAlter(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("ALTER TABLE ")
        self._schema._create_query(buffer)
        if self._table is not None:
            buffer.append(".")
            self._table._create_query(buffer)
