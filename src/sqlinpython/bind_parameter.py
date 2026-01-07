from __future__ import annotations

from abc import ABCMeta

from sqlinpython.expression import TermBeforeBracket, Value


class BindParameter(TermBeforeBracket, metaclass=ABCMeta):
    def __init__(self) -> None:
        pass


class BindParameterIndex(BindParameter):
    def __init__(self, i: int) -> None:
        self._i = i

    def _create_query(self) -> str:
        return f":{self._i}"


class BindParameterQ(BindParameter):
    def _create_query(self) -> str:
        return "?"


class BindParam:
    @staticmethod
    def Index(i: int) -> BindParameterIndex:
        return BindParameterIndex(i)

    q = BindParameterQ()


SplitPoint = Value | BindParameter
