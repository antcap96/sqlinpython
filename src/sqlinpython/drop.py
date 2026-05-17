from __future__ import annotations

from typing import Literal, override

from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.name import Name

# SPEC DROP TABLE: https://sqlite.org/lang_droptable.html
# SPEC DROP INDEX: https://sqlite.org/lang_dropindex.html
# SPEC DROP VIEW: https://sqlite.org/lang_dropview.html
# SPEC DROP TRIGGER: https://sqlite.org/lang_droptrigger.html


class _Table: ...


class _View: ...


class _Trigger: ...


class _Index: ...


class DropStatement[T: (_Table, _View, _Trigger, _Index)](CompleteSqlQuery):
    def __init__(self, prev: SqlElement, schema: Name, name: Name | None) -> None:
        self._prev = prev
        self._schema = schema
        self._name = name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._schema._create_query(buffer)
        if self._name is not None:
            buffer.append(".")
            self._name._create_query(buffer)


DropTableStatement = DropStatement[_Table]
DropViewStatement = DropStatement[_View]
DropTriggerStatement = DropStatement[_Trigger]
DropIndexStatement = DropStatement[_Index]


class DropIfExists[T: (_Table, _View, _Trigger, _Index)](SqlElement):
    def __init__(self, prev: DropTypeKeyword[T]) -> None:
        self._prev: DropTypeKeyword[T] = prev

    def __call__(
        self,
        schema: Name | str,
        name: Name | str | None = None,
        /,
    ) -> DropStatement[T]:
        if isinstance(schema, str):
            schema = Name(schema)
        if isinstance(name, str):
            name = Name(name)
        return DropStatement(self, schema, name)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" IF EXISTS")


class DropTypeKeyword[T: (_Table, _View, _Trigger, _Index)](SqlElement):
    def __init__(self, keyword: Literal["TABLE", "VIEW", "TRIGGER", "INDEX"]) -> None:
        self._keyword = keyword

    @property
    def IfExists(self) -> DropIfExists[T]:
        return DropIfExists(self)

    def __call__(
        self,
        schema: Name | str,
        name: Name | str | None = None,
        /,
    ) -> DropStatement[T]:
        if isinstance(schema, str):
            schema = Name(schema)
        if isinstance(name, str):
            name = Name(name)
        return DropStatement(self, schema, name)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append(f"DROP {self._keyword}")


class DropKeyword:
    @property
    def Table(self) -> DropTypeKeyword[_Table]:
        return DropTypeKeyword("TABLE")

    @property
    def View(self) -> DropTypeKeyword[_View]:
        return DropTypeKeyword("VIEW")

    @property
    def Trigger(self) -> DropTypeKeyword[_Trigger]:
        return DropTypeKeyword("TRIGGER")

    @property
    def Index(self) -> DropTypeKeyword[_Index]:
        return DropTypeKeyword("INDEX")


Drop = DropKeyword()
