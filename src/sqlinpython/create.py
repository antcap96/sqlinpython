import typing

from sqlinpython.base import SqlElement
from sqlinpython.create_index import CreateIndex
from sqlinpython.create_table import CreateTable
from sqlinpython.create_vtable import CreateVirtualTable


class CreateUnique(SqlElement):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    @property
    def Index(self) -> CreateIndex:
        return CreateIndex(self)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" UNIQUE")


class CreateTempTable(SqlElement):
    def __init__(self, prev: SqlElement, how: typing.Literal["TEMPORARY", "TEMP"]):
        self._prev = prev
        self._how = how

    @property
    def Table(self) -> CreateTable:
        return CreateTable(self)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._how}")


class CreateKeyword(CreateTempTable, CreateUnique):
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

    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("CREATE")


Create = CreateKeyword()
