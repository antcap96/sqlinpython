from __future__ import annotations

import re

from sqlinpython.base import SqlElement

UNQUOTED_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def quote_if_necessary(s: str, force_quote: bool = False) -> str:
    result = re.match(UNQUOTED_NAME_PATTERN, s)

    if force_quote or result is None:
        s = s.replace('"', '""')
        s = f'"{s}"'

    return s


class Name(SqlElement):
    def __init__(self, name: str, force_quote: bool = False) -> None:
        name = quote_if_necessary(name, force_quote)
        self._name = name

    def _create_query(self) -> str:
        return self._name
