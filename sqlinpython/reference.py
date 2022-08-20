from typing import Optional

from sqlinpython.base import SqlElement
from sqlinpython.name import Name


class SqlRef(SqlElement):
    def __init__(
        self, name: str | Name, base_name: Optional[str | Name] = None, /
    ) -> None:
        # TODO: maybe warn if name has '.'?
        if isinstance(name, str):
            name = Name(name)
        if isinstance(base_name, str):
            base_name = Name(base_name)

        schema_name = name if base_name is not None else None
        if base_name is None:
            base_name = name
        self._base_name = base_name
        self._schema_name = schema_name

    def _create_query(self) -> str:
        if self._schema_name:
            return (
                f"{self._schema_name._create_query()}.{self._base_name._create_query()}"
            )
        else:
            return self._base_name._create_query()


class SequenceRef(SqlRef):
    pass
