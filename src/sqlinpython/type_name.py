from sqlinpython.base import SqlElement
from sqlinpython.name import Name


# SPEC: https://sqlite.org/syntax/type-name.html
class CompleteTypeName(SqlElement):
    def __init__(self, prev: SqlElement, num1: int, num2: int | None = None):
        self._prev = prev
        self._num1 = num1
        self._num2 = num2

    def _create_query(self) -> str:
        if self._num2 is None:
            return f"{self._prev._create_query()}({self._num1})"
        else:
            return f"{self._prev._create_query()}({self._num1}, {self._num2})"


class TypeName(Name, CompleteTypeName):
    def __call__(self, num1: int, num2: int | None = None) -> CompleteTypeName:
        return CompleteTypeName(self, num1, num2)
