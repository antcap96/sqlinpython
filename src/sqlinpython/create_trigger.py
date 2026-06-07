from __future__ import annotations

from abc import ABC
from typing import Literal, override

from sqlinpython.base import CompleteSqlQuery, SqlElement, comma_separated
from sqlinpython.delete import DeleteStatement
from sqlinpython.expression import Expression
from sqlinpython.expression.literal import ExpressionOrLiteral, to_expr
from sqlinpython.insert import InsertStatement
from sqlinpython.name import Name
from sqlinpython.select_base import SelectStatement
from sqlinpython.update import UpdateStatement

# SPEC: https://sqlite.org/lang_createtrigger.html

TriggerBodyStmt = UpdateStatement | InsertStatement | DeleteStatement | SelectStatement


class CreateTriggerStatement(CompleteSqlQuery, ABC):
    pass


class CreateTriggerEnd(CreateTriggerStatement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append("END")


class IBeforeBegin(SqlElement, ABC):
    def Begin(
        self, *stmts: *tuple[TriggerBodyStmt, *tuple[TriggerBodyStmt, ...]]
    ) -> CreateTriggerBegin:
        return CreateTriggerBegin(self, stmts)


class CreateTriggerBegin(SqlElement):
    def __init__(self, prev: SqlElement, stmts: tuple[TriggerBodyStmt, ...]) -> None:
        self._prev = prev
        self._stmts = stmts

    @property
    def End(self) -> CreateTriggerEnd:
        return CreateTriggerEnd(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" BEGIN ")
        for stmt in self._stmts:
            stmt._create_query(buffer)
            buffer.append("; ")


class CreateTriggerWhen(IBeforeBegin):
    def __init__(self, prev: SqlElement, expr: Expression) -> None:
        self._prev = prev
        self._expr = expr

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" WHEN ")
        self._expr._create_query(buffer)


class IWithWhen(IBeforeBegin, ABC):
    def When(self, expr: ExpressionOrLiteral) -> CreateTriggerWhen:
        return CreateTriggerWhen(self, to_expr(expr))


class CreateTriggerForEachRow(IWithWhen):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" FOR EACH ROW")


class CreateTriggerOnTable(IWithWhen):
    def __init__(self, prev: SqlElement, table: Name) -> None:
        self._prev = prev
        self._table = table

    @property
    def ForEachRow(self) -> CreateTriggerForEachRow:
        return CreateTriggerForEachRow(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ON ")
        self._table._create_query(buffer)


class IBeforeOnTable(SqlElement, ABC):
    def On(self, table: Name | str, /) -> CreateTriggerOnTable:
        if isinstance(table, str):
            table = Name(table)
        return CreateTriggerOnTable(self, table)


class CreateTriggerUpdateOf(IBeforeOnTable):
    def __init__(self, prev: SqlElement, columns: tuple[Name, ...]) -> None:
        self._prev = prev
        self._columns = columns

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" OF ")
        comma_separated(buffer, self._columns)


class CreateTriggerUpdate(IBeforeOnTable):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def Of(
        self, *columns: *tuple[Name | str, *tuple[Name | str, ...]]
    ) -> CreateTriggerUpdateOf:
        resolved = tuple(c if isinstance(c, Name) else Name(c) for c in columns)
        return CreateTriggerUpdateOf(self, resolved)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" UPDATE")


class CreateTriggerEvent(IBeforeOnTable):
    def __init__(self, prev: SqlElement, event: Literal["DELETE", "INSERT"]) -> None:
        self._prev = prev
        self._event = event

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._event}")


class IEventClause(SqlElement, ABC):
    @property
    def Delete(self) -> CreateTriggerEvent:
        return CreateTriggerEvent(self, "DELETE")

    @property
    def Insert(self) -> CreateTriggerEvent:
        return CreateTriggerEvent(self, "INSERT")

    @property
    def Update(self) -> CreateTriggerUpdate:
        return CreateTriggerUpdate(self)


class CreateTriggerTiming(IEventClause):
    def __init__(
        self, prev: SqlElement, timing: Literal["BEFORE", "AFTER", "INSTEAD OF"]
    ) -> None:
        self._prev = prev
        self._timing = timing

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._timing}")


class CreateTriggerWithName(IEventClause):
    def __init__(self, prev: SqlElement, schema: Name, name: Name | None) -> None:
        self._prev = prev
        self._schema = schema
        self._name = name

    @property
    def Before(self) -> CreateTriggerTiming:
        return CreateTriggerTiming(self, "BEFORE")

    @property
    def After(self) -> CreateTriggerTiming:
        return CreateTriggerTiming(self, "AFTER")

    @property
    def InsteadOf(self) -> CreateTriggerTiming:
        return CreateTriggerTiming(self, "INSTEAD OF")

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._schema._create_query(buffer)
        if self._name is not None:
            buffer.append(".")
            self._name._create_query(buffer)


class CreateTriggerIfNotExists(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def __call__(
        self, schema: Name | str, name: Name | str | None = None, /
    ) -> CreateTriggerWithName:
        if isinstance(schema, str):
            schema = Name(schema)
        if isinstance(name, str):
            name = Name(name)
        return CreateTriggerWithName(self, schema, name)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IF NOT EXISTS")


class CreateTrigger(CreateTriggerIfNotExists):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def IfNotExists(self) -> CreateTriggerIfNotExists:
        return CreateTriggerIfNotExists(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" TRIGGER")
