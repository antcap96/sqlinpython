from abc import ABC
from typing import override

from sqlinpython.base import SqlElement
from sqlinpython.name import Name


# SPEC: https://sqlite.org/syntax/type-name.html
class CompleteTypeName(SqlElement, ABC):
    pass


class TypeNameWithArgs(CompleteTypeName):
    def __init__(self, prev: SqlElement, num1: int, num2: int | None = None):
        self._prev = prev
        self._num1 = num1
        self._num2 = num2

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        if self._num2 is None:
            buffer.append(f"({self._num1})")
        else:
            buffer.append(f"({self._num1}, {self._num2})")


class TypeName(CompleteTypeName):
    def __init__(self, *names: *tuple[str | Name, *tuple[str | Name, ...]]) -> None:
        self._names = tuple(Name(n) if isinstance(n, str) else n for n in names)

    def __call__(self, num1: int, num2: int | None = None) -> TypeNameWithArgs:
        return TypeNameWithArgs(self, num1, num2)

    @override
    def _create_query(self, buffer: list[str]) -> None:
        for i, name in enumerate(self._names):
            if i > 0:
                buffer.append(" ")
            name._create_query(buffer)
