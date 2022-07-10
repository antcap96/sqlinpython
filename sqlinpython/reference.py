from typing import Optional
from sqlinpython.base import SqlElement
import re

unquoted_name = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def quote_if_necessary(s: str, force_quote: bool = False) -> str:
    result = re.match(unquoted_name, s)

    if force_quote or result is None:
        s = s.replace('"', '""')
        s = f'"{s}"'

    return s


class SqlRef(SqlElement):
    def __init__(
        self, name: str, base_name: Optional[str] = None, /, force_quote: bool = False
    ) -> None:
        # TODO: maybe warn if name has '.'?
        name = quote_if_necessary(name, force_quote)
        if base_name is not None:
            base_name = quote_if_necessary(base_name, force_quote)

        schema_name = name if base_name is not None else None
        if base_name is None:
            base_name = name
        self._base_name = base_name
        self._schema_name = schema_name

    def _create_query(self) -> str:
        if self._schema_name:
            return f"{self._schema_name}.{self._base_name}"
        else:
            return self._base_name


class TableRef(SqlRef):
    pass


class SequenceRef(SqlRef):
    pass
