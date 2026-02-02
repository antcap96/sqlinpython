from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.name import Name


# SPEC: https://sqlite.org/lang_vacuum.html
class VacuumWithIntoFileName(CompleteSqlQuery):
    def __init__(self, prev: SqlElement, file_name: str) -> None:
        self._prev = prev
        self._file_name = file_name

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" INTO {self._file_name}")


class VacuumWithSchema(VacuumWithIntoFileName):
    def __init__(self, prev: SqlElement, schema_name: Name) -> None:
        self._prev = prev
        self._schema_name = schema_name

    def Into(self, file_name: str) -> VacuumWithIntoFileName:
        return VacuumWithIntoFileName(self, file_name)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._schema_name._create_query(buffer)


class VacuumKeyword(VacuumWithSchema):
    def __init__(self) -> None:
        pass

    def __call__(self, schema_name: Name | str) -> VacuumWithSchema:
        if isinstance(schema_name, str):
            schema_name = Name(schema_name)
        return VacuumWithSchema(self, schema_name)

    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("VACUUM")


Vacuum = VacuumKeyword()
