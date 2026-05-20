from abc import ABC
from typing import override

from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.name import Name


# SPEC: https://sqlite.org/lang_vacuum.html
class VacuumStatement(CompleteSqlQuery, ABC):
    pass


class VacuumWithIntoFileName(VacuumStatement):
    def __init__(self, prev: SqlElement, file_name: str) -> None:
        self._prev = prev
        self._file_name = file_name

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" INTO {self._file_name}")


class VacuumWithSchema(VacuumWithIntoFileName):
    def __init__(self, prev: SqlElement, schema: Name) -> None:
        self._prev = prev
        self._schema = schema

    def Into(self, file_name: str) -> VacuumWithIntoFileName:
        return VacuumWithIntoFileName(self, file_name)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._schema._create_query(buffer)


class VacuumKeyword(VacuumWithSchema):
    def __init__(self) -> None:
        pass

    def __call__(self, schema: Name | str) -> VacuumWithSchema:
        if isinstance(schema, str):
            schema = Name(schema)
        return VacuumWithSchema(self, schema)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("VACUUM")


Vacuum = VacuumKeyword()
