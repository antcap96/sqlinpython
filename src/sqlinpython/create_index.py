from __future__ import annotations


from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.expression import Expression
from sqlinpython.indexed_column import IndexedColumn
from sqlinpython.name import Name


class CreateIndexStatement(CompleteSqlQuery):
    pass


class CreateIndexWithWhere(CreateIndexStatement):
    def __init__(self, prev: SqlElement, expr: Expression):
        self._prev = prev
        self._expr = expr

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" WHERE ")
        self._expr._create_query(buffer)


class CreateIndexOnTable(CreateIndexStatement):
    def __init__(
        self,
        prev: SqlElement,
        table_name: Name,
        columns: tuple[IndexedColumn, ...],
    ):
        self._prev = prev
        self._table_name = table_name
        self._columns = columns

    def Where(self, expr: Expression) -> CreateIndexWithWhere:
        return CreateIndexWithWhere(self, expr)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ON ")
        self._table_name._create_query(buffer)
        buffer.append(" (")
        for i, col in enumerate(self._columns):
            if i > 0:
                buffer.append(", ")
            col._create_query(buffer)
        buffer.append(")")


class CreateIndexWithName(SqlElement):
    def __init__(self, prev: SqlElement, schema_name: Name, index_name: Name | None):
        self._prev = prev
        self._schema_name = schema_name
        self._index_name = index_name

    def On(
        self,
        table_name: str | Name,
        first_col: IndexedColumn,
        *rest_cols: IndexedColumn,
    ) -> CreateIndexOnTable:
        if isinstance(table_name, str):
            table_name = Name(table_name)
        return CreateIndexOnTable(self, table_name, (first_col, *rest_cols))

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._schema_name._create_query(buffer)
        if self._index_name is not None:
            buffer.append(".")
            self._index_name._create_query(buffer)


class CreateIndexIfNotExists(CreateIndexWithName):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def __call__(
        self, schema_name: str | Name, index_name: str | Name | None = None
    ) -> CreateIndexWithName:
        if isinstance(schema_name, str):
            schema_name = Name(schema_name)
        if isinstance(index_name, str):
            index_name = Name(index_name)
        return CreateIndexWithName(self, schema_name, index_name)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IF NOT EXISTS")


class CreateIndex(CreateIndexIfNotExists):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @property
    def IfNotExists(self) -> CreateIndexIfNotExists:
        return CreateIndexIfNotExists(self)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" INDEX")
