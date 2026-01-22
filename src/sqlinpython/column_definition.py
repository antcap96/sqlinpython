from __future__ import annotations

import typing

from sqlinpython.base import NotImplementedSqlElement, SqlElement
from sqlinpython.expression import Expression, Literal
from sqlinpython.name import Name
from sqlinpython.type_name import CompleteTypeName


# SPEC: https://sqlite.org/syntax/column-def.html
class ColumnDefinition(SqlElement):
    """To construct a ColumnDefinition, start from a ColumnName"""

    pass


class WithGeneratedAlways(SqlElement):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def As(self, expression: Expression):
        return GeneratedAlwaysAs(self, expression)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} GENERATED ALWAYS"


class ColumnConstraintWithName(WithGeneratedAlways):
    def __init__(self, prev: SqlElement, name: Name):
        self._prev = prev
        self._name = name

    @property
    def PrimaryKey(self) -> ColumnConstraintPrimaryKey:
        return ColumnConstraintPrimaryKey(self)

    # Spec: https://sqlite.org/syntax/conflict-clause.html
    @property
    def NotNull(self) -> WithNotNull:
        return WithNotNull(self)

    @property
    def Unique(self) -> WithUnique:
        return WithUnique(self)

    def Check(self, expression: Expression) -> WithCheck:
        return WithCheck(self, expression)

    def Default(self, value: int | Literal | Expression) -> WithDefault:
        return WithDefault(self, value)

    def Collate(self, collation_name: Name | str) -> WithCollate:
        if isinstance(collation_name, str):
            collation_name = Name(collation_name)
        return WithCollate(self, collation_name)

    # SPEC: https://sqlite.org/syntax/foreign-key-clause.html
    def References(self, foreign_table_name: Name | str) -> WithReferences:
        if isinstance(foreign_table_name, str):
            foreign_table_name = Name(foreign_table_name)
        # return WithReferences(self, foreign_table_name)
        return WithReferences("TODO")

    @property
    def GeneratedAlways(self) -> WithGeneratedAlways:
        return WithGeneratedAlways(self)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} CONSTRAINT {self._name._create_query()}"


class ColumnNameWithType(ColumnDefinition, ColumnConstraintWithName):
    def __init__(self, prev: SqlElement, type_name: CompleteTypeName):
        self._prev = prev
        self._type_name = type_name

    def Constraint(self, name: Name | str) -> ColumnConstraintWithName:
        if isinstance(name, str):
            name = Name(name)
        return ColumnConstraintWithName(self, name)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._type_name._create_query()}"


class WithReferences(NotImplementedSqlElement):
    pass


class WithCheck(ColumnNameWithType):
    def __init__(self, prev: SqlElement, check_expression: Expression):
        self._prev = prev
        self._check_expression = check_expression

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} CHECK ({self._check_expression._create_query()})"


class WithDefault(ColumnNameWithType):
    # TODO: Not sure if possible to pass +1 somehow but should be accepted
    def __init__(self, prev: SqlElement, default_value: Expression | Literal | int):
        self._prev = prev
        self._default_value = default_value

    def _create_query(self) -> str:
        if isinstance(self._default_value, int):
            return f"{self._prev._create_query()} DEFAULT {self._default_value}"
        return f"{self._prev._create_query()} DEFAULT {self._default_value._create_query()}"


class WithCollate(ColumnNameWithType):
    def __init__(self, prev: SqlElement, collation_name: Name):
        self._prev = prev
        self._collation_name = collation_name

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} COLLATE {self._collation_name._create_query()}"


class ConflictClauseAutoIncrement(ColumnNameWithType):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} AUTOINCREMENT"


class OnConflictAction2(ColumnNameWithType):
    def __init__(
        self,
        prev: SqlElement,
        action: typing.Literal["ROLLBACK", "ABORT", "FAIL", "IGNORE", "REPLACE"],
    ):
        self._prev = prev
        self._action = action

    @property
    def AutoIncrement(self) -> ConflictClauseAutoIncrement:
        return ConflictClauseAutoIncrement(self)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._action}"


class OnConflict2(SqlElement):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @property
    def Rollback(self) -> OnConflictAction2:
        return OnConflictAction2(self, "ROLLBACK")

    @property
    def Abort(self) -> OnConflictAction2:
        return OnConflictAction2(self, "ABORT")

    @property
    def Fail(self) -> OnConflictAction2:
        return OnConflictAction2(self, "FAIL")

    @property
    def Ignore(self) -> OnConflictAction2:
        return OnConflictAction2(self, "IGNORE")

    @property
    def Replace(self) -> OnConflictAction2:
        return OnConflictAction2(self, "REPLACE")

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} ON CONFLICT"


class ConflictClause2(OnConflictAction2):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @property
    def OnConflict(self) -> OnConflict2:
        return OnConflict2(self)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()}"


class ColumnConstraintPrimaryKeyOrdered(ConflictClause2):
    def __init__(self, prev: SqlElement, ascending: bool):
        self._prev = prev
        self._ascending = ascending

    def _create_query(self) -> str:
        how = "ASC" if self._ascending else "DESC"
        return f"{self._prev._create_query()} {how}"


class ColumnConstraintPrimaryKey(ColumnConstraintPrimaryKeyOrdered):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @property
    def Asc(self) -> ColumnConstraintPrimaryKeyOrdered:
        return ColumnConstraintPrimaryKeyOrdered(self, True)

    @property
    def Desc(self) -> ColumnConstraintPrimaryKeyOrdered:
        return ColumnConstraintPrimaryKeyOrdered(self, False)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} PRIMARY KEY"


class OnConflictAction(ColumnNameWithType):
    def __init__(
        self,
        prev: SqlElement,
        action: typing.Literal["ROLLBACK", "ABORT", "FAIL", "IGNORE", "REPLACE"],
    ):
        self._prev = prev
        self._action = action

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._action}"


class WithOnConflict(SqlElement):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @property
    def Rollback(self) -> OnConflictAction:
        return OnConflictAction(self, "ROLLBACK")

    @property
    def Abort(self) -> OnConflictAction:
        return OnConflictAction(self, "ABORT")

    @property
    def Fail(self) -> OnConflictAction:
        return OnConflictAction(self, "FAIL")

    @property
    def Ignore(self) -> OnConflictAction:
        return OnConflictAction(self, "IGNORE")

    @property
    def Replace(self) -> OnConflictAction:
        return OnConflictAction(self, "REPLACE")

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} ON CONFLICT"


class ConflictClause(OnConflictAction):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @property
    def OnConflict(self) -> WithOnConflict:
        return WithOnConflict(self)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()}"


class WithNotNull(ConflictClause):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} NOT NULL"


class WithUnique(ConflictClause):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} UNIQUE"


class GeneratedAlwaysAsHow(ColumnNameWithType):
    def __init__(self, prev: SqlElement, how: str):
        self._prev = prev
        self._how = how

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._how}"


class GeneratedAlwaysAs(GeneratedAlwaysAsHow):
    def __init__(self, prev: SqlElement, expression: Expression):
        self._prev = prev
        self._expression = expression

    @property
    def Stored(self):
        return GeneratedAlwaysAsHow(self, "STORED")

    @property
    def Virtual(self):
        return GeneratedAlwaysAsHow(self, "VIRTUAL")

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} AS ({self._expression._create_query()})"
