import typing

from sqlinpython.base import CompleteSqlQuery, NotImplementedSqlElement, SqlElement
from sqlinpython.column_definition import ColumnDefinition
from sqlinpython.name import Name


# Spec https://sqlite.org/syntax/select-stmt.html
class SelectStatement(NotImplementedSqlElement):
    pass


# SPEC: https://sqlite.org/syntax/table-constraint.html
class TableConstraint(NotImplementedSqlElement):
    pass


# SPEC: https://sqlite.org/syntax/create-table-stmt.html
class CreateTableStatement(CompleteSqlQuery):
    pass


class CreateTableAs(CreateTableStatement):
    def __init__(self, prev: SqlElement, select_stmt: SelectStatement):
        self._prev = prev
        self._select_stmt = select_stmt

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} AS {self._select_stmt._create_query()}"


class AddComma(SqlElement):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()},"


class CreateTableWithOptions(CreateTableStatement):
    def __init__(
        self, prev: SqlElement, option: typing.Literal["WITHOUT ROWID", "STRICT"]
    ):
        self._prev = prev
        self._option = option

    @property
    def WithoutRowId(self):
        return CreateTableWithOptions(AddComma(self), "WITHOUT ROWID")

    @property
    def Strict(self):
        return CreateTableWithOptions(AddComma(self), "STRICT")

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._option}"


class CreateTableWithDefinitions(CreateTableStatement):
    def __init__(
        self, prev: SqlElement, args: tuple[ColumnDefinition | TableConstraint, ...]
    ):
        self._prev = prev
        self._args = args

    @property
    def WithoutRowId(self):
        return CreateTableWithOptions(self, "WITHOUT ROWID")

    @property
    def Strict(self):
        return CreateTableWithOptions(self, "STRICT")

    def _create_query(self) -> str:
        text = ", ".join(col._create_query() for col in self._args)
        return f"{self._prev._create_query()} ({text})"


class CreateTableWithName(SqlElement):
    def __init__(self, prev: SqlElement, schema_name: Name, table_name: Name | None):
        self._prev = prev
        self._schema_name = schema_name
        self._table_name = table_name

    def As(self, select_stmt: SelectStatement):
        return CreateTableAs(self, select_stmt)

    def __call__(
        self, first_col: ColumnDefinition, *rest: ColumnDefinition | TableConstraint
    ):
        # TODO: Validate that any table constraints are at the end
        return CreateTableWithDefinitions(self, (first_col, *rest))

    def _create_query(self) -> str:
        if self._table_name is None:
            return f"{self._prev._create_query()} {self._schema_name._create_query()}"
        else:
            return f"{self._prev._create_query()} {self._schema_name._create_query()}.{self._table_name._create_query()}"


class CreateTableIfNotExists(SqlElement):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def __call__(self, schema_name: str | Name, table_name: str | Name | None = None):
        if isinstance(schema_name, str):
            schema_name = Name(schema_name)
        if isinstance(table_name, str):
            table_name = Name(table_name)
        return CreateTableWithName(self, schema_name, table_name)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} IF NOT EXISTS"


class CreateTable(CreateTableIfNotExists):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @property
    def IfNotExists(self):
        return CreateTableIfNotExists(self)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} TABLE"


class CreateTempTable(SqlElement):
    def __init__(self, prev: SqlElement, how: typing.Literal["TEMPORARY", "TEMP"]):
        self._prev = prev
        self._how = how

    @property
    def Table(self):
        return CreateTable(self)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._how}"


class CreateKeyword(CreateTempTable):
    def __init__(self):
        pass

    @property
    def Temp(self):
        return CreateTempTable(self, "TEMP")

    @property
    def Temporary(self):
        return CreateTempTable(self, "TEMPORARY")

    def _create_query(self) -> str:
        return "CREATE"


Create = CreateKeyword()
