from __future__ import annotations


from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.name import Name


# Spec: https://sqlite.org/lang_createvtab.html
class CreateVirtualTableStatement(CompleteSqlQuery):
    pass


class CreateVirtualTableWithArgs(CreateVirtualTableStatement):
    def __init__(self, prev: SqlElement, args: tuple[str, ...]):
        self._prev = prev
        self._args = args

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append("(")
        for i, arg in enumerate(self._args):
            if i > 0:
                buffer.append(", ")
            buffer.append(arg)
        buffer.append(")")


class CreateVirtualTableUsing(CreateVirtualTableStatement):
    def __init__(self, prev: SqlElement, module_name: Name):
        self._prev = prev
        self._module_name = module_name

    def __call__(self, *args: str) -> CreateVirtualTableWithArgs:
        return CreateVirtualTableWithArgs(self, args)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" USING ")
        self._module_name._create_query(buffer)


class CreateVirtualTableWithName(SqlElement):
    def __init__(self, prev: SqlElement, schema_name: Name, table_name: Name | None):
        self._prev = prev
        self._schema_name = schema_name
        self._table_name = table_name

    def Using(self, module_name: str | Name) -> CreateVirtualTableUsing:
        if isinstance(module_name, str):
            module_name = Name(module_name)
        return CreateVirtualTableUsing(self, module_name)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._schema_name._create_query(buffer)
        if self._table_name is not None:
            buffer.append(".")
            self._table_name._create_query(buffer)


class CreateVirtualTableIfNotExists(SqlElement):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def __call__(
        self, schema_name: str | Name, table_name: str | Name | None = None
    ) -> CreateVirtualTableWithName:
        if isinstance(schema_name, str):
            schema_name = Name(schema_name)
        if isinstance(table_name, str):
            table_name = Name(table_name)
        return CreateVirtualTableWithName(self, schema_name, table_name)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IF NOT EXISTS")


class CreateVirtualTable(CreateVirtualTableIfNotExists):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @property
    def IfNotExists(self) -> CreateVirtualTableIfNotExists:
        return CreateVirtualTableIfNotExists(self)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" VIRTUAL TABLE")
