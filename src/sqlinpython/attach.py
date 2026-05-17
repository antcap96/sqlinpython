from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.expression import Expression
from sqlinpython.name import Name


# SPEC: https://sqlite.org/lang_attach.html
class AttachStatement(CompleteSqlQuery, ABC):
    pass


class AttachComplete(AttachStatement):
    def __init__(self, prev: SqlElement, schema_name: Name) -> None:
        self._prev = prev
        self._schema_name = schema_name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" AS ")
        self._schema_name._create_query(buffer)


class AttachWithExpr(SqlElement):
    def __init__(self, prev: SqlElement, file_expr: Expression) -> None:
        self._prev = prev
        self._file_expr = file_expr

    def As(self, schema_name: Name | str) -> AttachComplete:
        if isinstance(schema_name, str):
            schema_name = Name(schema_name)
        return AttachComplete(self, schema_name)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._file_expr._create_query(buffer)


class IAttachCall(SqlElement, ABC):
    def __call__(self, file_expr: Expression) -> AttachWithExpr:
        return AttachWithExpr(self, file_expr)


class AttachDatabaseKeyword(IAttachCall):
    def __init__(self, prev: AttachKeyword) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" DATABASE")


class AttachKeyword(IAttachCall):
    @property
    def Database(self) -> AttachDatabaseKeyword:
        return AttachDatabaseKeyword(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("ATTACH")


Attach = AttachKeyword()
