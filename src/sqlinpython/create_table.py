from __future__ import annotations

import typing


from sqlinpython.base import CompleteSqlQuery, NotImplementedSqlElement, SqlElement
from sqlinpython.column_definition import ColumnDefinition
from sqlinpython.name import Name
from sqlinpython.table_constraint import TableConstraint


# Spec https://sqlite.org/syntax/select-stmt.html
class SelectStatement(NotImplementedSqlElement):
    pass


# SPEC: https://sqlite.org/syntax/create-table-stmt.html
class CreateTableStatement(CompleteSqlQuery):
    pass


class CreateTableAs(CreateTableStatement):
    def __init__(self, prev: SqlElement, select_stmt: SelectStatement):
        self._prev = prev
        self._select_stmt = select_stmt

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" AS ")
        self._select_stmt._create_query(buffer)


class AddComma(SqlElement):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(",")


class CreateTableWithOptions(CreateTableStatement):
    def __init__(
        self, prev: SqlElement, option: typing.Literal["WITHOUT ROWID", "STRICT"]
    ):
        self._prev = prev
        self._option = option

    @property
    def WithoutRowId(self) -> CreateTableWithOptions:
        return CreateTableWithOptions(AddComma(self), "WITHOUT ROWID")

    @property
    def Strict(self) -> CreateTableWithOptions:
        return CreateTableWithOptions(AddComma(self), "STRICT")

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._option}")


class CreateTableWithDefinitions(CreateTableStatement):
    def __init__(
        self, prev: SqlElement, args: tuple[ColumnDefinition | TableConstraint, ...]
    ):
        self._prev = prev
        self._args = args

    @property
    def WithoutRowId(self) -> CreateTableWithOptions:
        return CreateTableWithOptions(self, "WITHOUT ROWID")

    @property
    def Strict(self) -> CreateTableWithOptions:
        return CreateTableWithOptions(self, "STRICT")

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" (")
        for i, col in enumerate(self._args):
            if i > 0:
                buffer.append(", ")
            col._create_query(buffer)
        buffer.append(")")


class CreateTableWithName(SqlElement):
    def __init__(self, prev: SqlElement, schema_name: Name, table_name: Name | None):
        self._prev = prev
        self._schema_name = schema_name
        self._table_name = table_name

    def As(self, select_stmt: SelectStatement) -> CreateTableAs:
        return CreateTableAs(self, select_stmt)

    def __call__(
        self, first_col: ColumnDefinition, *rest: ColumnDefinition | TableConstraint
    ) -> CreateTableWithDefinitions:
        # TODO: Validate that any table constraints are at the end
        return CreateTableWithDefinitions(self, (first_col, *rest))

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._schema_name._create_query(buffer)
        if self._table_name is not None:
            buffer.append(".")
            self._table_name._create_query(buffer)


class CreateTableIfNotExists(SqlElement):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def __call__(
        self, schema_name: str | Name, table_name: str | Name | None = None
    ) -> CreateTableWithName:
        if isinstance(schema_name, str):
            schema_name = Name(schema_name)
        if isinstance(table_name, str):
            table_name = Name(table_name)
        return CreateTableWithName(self, schema_name, table_name)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IF NOT EXISTS")


class CreateTable(CreateTableIfNotExists):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @property
    def IfNotExists(self) -> CreateTableIfNotExists:
        return CreateTableIfNotExists(self)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" TABLE")


class CreateTempTable(SqlElement):
    def __init__(self, prev: SqlElement, how: typing.Literal["TEMPORARY", "TEMP"]):
        self._prev = prev
        self._how = how

    @property
    def Table(self) -> CreateTable:
        return CreateTable(self)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._how}")


class CreateKeyword(CreateTempTable):
    def __init__(self) -> None:
        pass

    @property
    def Temp(self) -> CreateTempTable:
        return CreateTempTable(self, "TEMP")

    @property
    def Temporary(self) -> CreateTempTable:
        return CreateTempTable(self, "TEMPORARY")

    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("CREATE")


Create = CreateKeyword()
