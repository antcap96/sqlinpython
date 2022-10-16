from __future__ import annotations

from abc import ABCMeta

from sqlinpython.base import SqlElement
from sqlinpython.sequence.core import SequenceRef


class SequenceQuery(SqlElement, metaclass=ABCMeta):
    pass


class SequenceWithFor(SequenceQuery):
    def __init__(self, prev: SqlElement, sequence_ref: SequenceRef) -> None:
        self._prev = prev
        self._sequence_ref = sequence_ref

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} FOR {self._sequence_ref._create_query()}"


class SequenceWithValueMixin(SqlElement, metaclass=ABCMeta):
    def For(self, sequence_ref: SequenceRef) -> SequenceWithFor:
        return SequenceWithFor(self, sequence_ref)


class SequenceWithValue(SequenceWithValueMixin):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} VALUE"


class SequenceWithValues(SequenceWithValueMixin):
    def __init__(self, prev: SqlElement, n: int) -> None:
        self._prev = prev
        self._n = n

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._n} VALUES"


class SequenceStartMixin(SqlElement, metaclass=ABCMeta):
    @property
    def Value(self) -> SequenceWithValue:
        return SequenceWithValue(self)

    def Values(self, n: int) -> SequenceWithValues:
        return SequenceWithValues(self, n)


class NextKeyword(SequenceStartMixin):
    def __init__(self) -> None:
        pass

    def _create_query(self) -> str:
        return f"NEXT"


class CurrentKeyword(SequenceStartMixin):
    def __init__(self) -> None:
        pass

    def _create_query(self) -> str:
        return f"CURRENT"


Next = NextKeyword()
Current = CurrentKeyword()
