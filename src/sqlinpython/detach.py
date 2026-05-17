from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.name import Name


# SPEC: https://sqlite.org/lang_detach.html
class DetachStatement(CompleteSqlQuery, ABC):
    pass


class DetachComplete(DetachStatement):
    def __init__(self, prev: SqlElement, schema_name: Name) -> None:
        self._prev = prev
        self._schema_name = schema_name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._schema_name._create_query(buffer)


class IDetachCall(SqlElement, ABC):
    def __call__(self, schema_name: Name | str) -> DetachComplete:
        if isinstance(schema_name, str):
            schema_name = Name(schema_name)
        return DetachComplete(self, schema_name)


class DetachDatabaseKeyword(IDetachCall):
    def __init__(self, prev: DetachKeyword) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" DATABASE")


class DetachKeyword(IDetachCall):
    def __init__(self) -> None:
        self._database = DetachDatabaseKeyword(self)

    @property
    def Database(self) -> DetachDatabaseKeyword:
        return self._database

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("DETACH")


Detach = DetachKeyword()
