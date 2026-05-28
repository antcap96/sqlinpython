import typing
from abc import ABC
from typing import override

from sqlinpython.base import SqlElement
from sqlinpython.create_index import CreateIndex
from sqlinpython.create_table import CreateTable
from sqlinpython.create_trigger import CreateTrigger
from sqlinpython.create_view import CreateView
from sqlinpython.create_vtable import CreateVirtualTable

# SPEC: https://sqlite.org/lang_createtable.html
# SPEC: https://sqlite.org/lang_createindex.html
# SPEC: https://sqlite.org/lang_createvtab.html
# SPEC: https://sqlite.org/lang_createview.html


class ICreateUnique(SqlElement, ABC):
    @property
    def Index(self) -> CreateIndex:
        return CreateIndex(self)


class CreateUnique(ICreateUnique):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" UNIQUE")


class ICreateTemp(SqlElement, ABC):
    @property
    def Table(self) -> CreateTable:
        return CreateTable(self)

    @property
    def Trigger(self) -> CreateTrigger:
        return CreateTrigger(self)

    @property
    def View(self) -> CreateView:
        return CreateView(self)


class CreateTempTable(ICreateTemp):
    def __init__(self, prev: SqlElement, how: typing.Literal["TEMPORARY", "TEMP"]):
        self._prev = prev
        self._how = how

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._how}")


class CreateKeyword(ICreateTemp, ICreateUnique):
    def __init__(self) -> None:
        pass

    @property
    def Unique(self) -> CreateUnique:
        return CreateUnique(self)

    @property
    def Temp(self) -> CreateTempTable:
        return CreateTempTable(self, "TEMP")

    @property
    def Temporary(self) -> CreateTempTable:
        return CreateTempTable(self, "TEMPORARY")

    @property
    def VirtualTable(self) -> CreateVirtualTable:
        return CreateVirtualTable(self)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("CREATE")


Create = CreateKeyword()
