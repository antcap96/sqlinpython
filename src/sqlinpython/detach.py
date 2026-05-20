from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.name import Name


# SPEC: https://sqlite.org/lang_detach.html
class DetachStatement(CompleteSqlQuery, ABC):
    pass


class DetachComplete(DetachStatement):
    def __init__(self, prev: SqlElement, schema: Name) -> None:
        self._prev = prev
        self._schema = schema

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._schema._create_query(buffer)


class IDetachCall(SqlElement, ABC):
    def __call__(self, schema: Name | str) -> DetachComplete:
        if isinstance(schema, str):
            schema = Name(schema)
        return DetachComplete(self, schema)


class DetachDatabaseKeyword(IDetachCall):
    def __init__(self, prev: DetachKeyword) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" DATABASE")


class DetachKeyword(IDetachCall):
    @property
    def Database(self) -> DetachDatabaseKeyword:
        return DetachDatabaseKeyword(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("DETACH")


Detach = DetachKeyword()
