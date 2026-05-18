from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.name import Name


# SPEC: https://sqlite.org/pragma.html
class PragmaStatement(CompleteSqlQuery, ABC):
    pass


class PragmaWithValue(PragmaStatement):
    def __init__(
        self, prev: SqlElement, value: bool | int | str | Name, eq: bool
    ) -> None:
        self._prev = prev
        self._value = value
        self._eq = eq

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" = " if self._eq else " (")
        value = self._value
        if isinstance(value, bool):
            buffer.append("true" if value else "false")
        elif isinstance(value, int):
            buffer.append(str(value))
        elif isinstance(value, str):
            Name(value)._create_query(buffer)
        else:
            value._create_query(buffer)
        if not self._eq:
            buffer.append(")")


class PragmaName(PragmaStatement):
    def __init__(self, prev: SqlElement, schema: Name, name: Name | None) -> None:
        self._prev = prev
        self._schema = schema
        self._name = name

    def __call__(
        self,
        value: bool | int | str | Name,
        *,
        eq: bool = False,
    ) -> PragmaWithValue:
        return PragmaWithValue(self, value, eq)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._schema._create_query(buffer)
        if self._name is not None:
            buffer.append(".")
            self._name._create_query(buffer)


class PragmaKeyword(SqlElement):
    def __init__(self) -> None:
        pass

    def __call__(
        self,
        schema: Name | str,
        name: Name | str | None = None,
        /,
    ) -> PragmaName:
        if isinstance(schema, str):
            schema = Name(schema)
        if isinstance(name, str):
            name = Name(name)
        return PragmaName(self, schema, name)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("PRAGMA")


Pragma = PragmaKeyword()
