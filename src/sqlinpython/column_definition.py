from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, overload, override

from sqlinpython.base import SqlElement
from sqlinpython.conflict_clause import OnConflict_, OnConflictAction
from sqlinpython.expression import Expression, ExpressionOrLiteral, Literal, to_expr
from sqlinpython.name import Name
from sqlinpython.type_name import CompleteTypeName

if TYPE_CHECKING:
    from sqlinpython.column_foreign_key_clause import ColumnReferences_


# SPEC: https://sqlite.org/syntax/column-def.html
class ColumnDefinition(SqlElement, ABC):
    """To construct a ColumnDefinition, start from a ColumnDef"""

    pass


class IColumnConstraintWithName(SqlElement, ABC):
    @property
    def PrimaryKey(self) -> ColumnConstraintPrimaryKey:
        return ColumnConstraintPrimaryKey(self)

    @property
    def NotNull(self) -> WithNotNull:
        return WithNotNull(self)

    @property
    def Unique(self) -> WithUnique:
        return WithUnique(self)

    def Check(self, expression: ExpressionOrLiteral) -> WithCheck:
        return WithCheck(self, to_expr(expression))

    @overload
    def Default(
        self,
        value: int,
        *,
        explicit_sign: bool = False,
        force_parenthesis: bool = False,
    ) -> WithDefault: ...
    @overload
    def Default(
        self, value: Literal | Expression, *, force_parenthesis: bool = False
    ) -> WithDefault: ...
    def Default(
        self,
        value: int | Literal | Expression,
        *,
        explicit_sign: bool = False,
        force_parenthesis: bool = False,
    ) -> WithDefault:
        return WithDefault(
            self,
            value,
            explicit_sign=explicit_sign,
            force_parenthesis=force_parenthesis,
        )

    def Collate(self, collation_name: Name | str, /) -> WithCollate:
        if isinstance(collation_name, str):
            collation_name = Name(collation_name)
        return WithCollate(self, collation_name)

    # SPEC: https://sqlite.org/syntax/foreign-key-clause.html
    def References(self, foreign_table_name: Name | str) -> ColumnReferences_:
        from sqlinpython.column_foreign_key_clause import ColumnReferences_

        if isinstance(foreign_table_name, str):
            foreign_table_name = Name(foreign_table_name)

        return ColumnReferences_(self, foreign_table_name)

    @property
    def GeneratedAlways(self) -> WithGeneratedAlways:
        return WithGeneratedAlways(self)

    # SPEC: https://sqlite.org/syntax/column-constraint.html
    # GENERATED ALWAYS is optional; this shortcut omits it
    def As(self, expression: ExpressionOrLiteral, /) -> GeneratedAlwaysAs:
        return GeneratedAlwaysAs(self, to_expr(expression))


class IColumnConstraint(ColumnDefinition, IColumnConstraintWithName, ABC):
    def Constraint(self, name: Name | str) -> ColumnConstraintWithName:
        if isinstance(name, str):
            name = Name(name)
        return ColumnConstraintWithName(self, name)


class ConflictClauseAutoIncrement(IColumnConstraint):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" AUTOINCREMENT")


class ConflictClauseMaybeAutoIncrement(OnConflictAction, IColumnConstraint):
    @property
    def AutoIncrement(self) -> ConflictClauseAutoIncrement:
        return ConflictClauseAutoIncrement(self)


class IPrimaryKeyConflict(ConflictClauseMaybeAutoIncrement, ABC):
    @property
    def OnConflict(self) -> OnConflict_[ConflictClauseMaybeAutoIncrement]:
        return OnConflict_(ConflictClauseMaybeAutoIncrement, self)


class ColumnConstraintPrimaryKeyOrdered(IPrimaryKeyConflict):
    def __init__(self, prev: SqlElement, ascending: bool):
        self._prev = prev
        self._ascending = ascending

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        if self._ascending:
            buffer.append(" ASC")
        else:
            buffer.append(" DESC")


class ColumnConstraintPrimaryKey(IPrimaryKeyConflict):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @property
    def Asc(self) -> ColumnConstraintPrimaryKeyOrdered:
        return ColumnConstraintPrimaryKeyOrdered(self, True)

    @property
    def Desc(self) -> ColumnConstraintPrimaryKeyOrdered:
        return ColumnConstraintPrimaryKeyOrdered(self, False)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" PRIMARY KEY")


class ConstraintWithClause(OnConflictAction, IColumnConstraint, ABC):
    pass


class IConflictClause(ConstraintWithClause, ABC):
    @property
    def OnConflict(self) -> OnConflict_[ConstraintWithClause]:
        return OnConflict_(ConstraintWithClause, self)


class WithNotNull(IConflictClause):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" NOT NULL")


class WithUnique(IConflictClause):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" UNIQUE")


class WithCheck(IColumnConstraint):
    def __init__(self, prev: SqlElement, check_expression: Expression):
        self._prev = prev
        self._check_expression = check_expression

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" CHECK (")
        self._check_expression._create_query(buffer)
        buffer.append(")")


class WithDefault(IColumnConstraint):
    def __init__(
        self,
        prev: SqlElement,
        default_value: Expression | Literal | int,
        *,
        explicit_sign: bool = False,
        force_parenthesis: bool = False,
    ):
        self._prev = prev
        self._default_value = default_value
        self._explicit_sign = explicit_sign
        self._force_parenthesis = force_parenthesis

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" DEFAULT ")
        if isinstance(self._default_value, int):
            val = (
                f"{self._default_value:+}"
                if self._explicit_sign
                else str(self._default_value)
            )
            buffer.append(f"({val})" if self._force_parenthesis else val)
        elif self._force_parenthesis or not isinstance(self._default_value, Literal):
            buffer.append("(")
            self._default_value._create_query(buffer)
            buffer.append(")")
        else:
            self._default_value._create_query(buffer)


class WithCollate(IColumnConstraint):
    def __init__(self, prev: SqlElement, collation_name: Name):
        self._prev = prev
        self._collation_name = collation_name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" COLLATE ")
        self._collation_name._create_query(buffer)


class GeneratedAlwaysAsHow(IColumnConstraint):
    def __init__(self, prev: SqlElement, how: str):
        self._prev = prev
        self._how = how

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._how}")


class GeneratedAlwaysAs(IColumnConstraint):
    def __init__(self, prev: SqlElement, expression: Expression):
        self._prev = prev
        self._expression = expression

    @property
    def Stored(self) -> GeneratedAlwaysAsHow:
        return GeneratedAlwaysAsHow(self, "STORED")

    @property
    def Virtual(self) -> GeneratedAlwaysAsHow:
        return GeneratedAlwaysAsHow(self, "VIRTUAL")

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" AS (")
        self._expression._create_query(buffer)
        buffer.append(")")


class WithGeneratedAlways(SqlElement):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def As(self, expression: ExpressionOrLiteral, /) -> GeneratedAlwaysAs:
        return GeneratedAlwaysAs(self, to_expr(expression))

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" GENERATED ALWAYS")


class ColumnConstraintWithName(IColumnConstraintWithName):
    def __init__(self, prev: SqlElement, name: Name):
        self._prev = prev
        self._name = name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" CONSTRAINT ")
        self._name._create_query(buffer)


class ColumnNameWithType(IColumnConstraint):
    def __init__(self, prev: SqlElement, type_name: CompleteTypeName):
        self._prev = prev
        self._type_name = type_name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._type_name._create_query(buffer)


class ColumnDef(IColumnConstraint):
    """DDL entry point for a column definition: ColumnDef('a')(TypeName('INT'))."""

    def __init__(self, name: Name | str, /) -> None:
        if isinstance(name, str):
            name = Name(name)
        self._name = name

    def __call__(self, type_name: CompleteTypeName) -> ColumnNameWithType:
        return ColumnNameWithType(self, type_name)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._name._create_query(buffer)
