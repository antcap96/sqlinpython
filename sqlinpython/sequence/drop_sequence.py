from __future__ import annotations

from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.sequence.core import SequenceRef


class DropSequenceWithSequenceRef(CompleteSqlQuery):
    def __init__(self, prev: SqlElement, sequence_ref: SequenceRef) -> None:
        self._prev = prev
        self._sequence_ref = sequence_ref

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._sequence_ref._create_query()}"


class DropSequenceWithIfExists(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} IF EXISTS"

    def __call__(self, table_ref: SequenceRef) -> DropSequenceWithSequenceRef:
        return DropSequenceWithSequenceRef(self, table_ref)


class DropSequenceKeyword(DropSequenceWithIfExists):
    def __init__(self) -> None:
        pass

    def _create_query(self) -> str:
        return "DROP SEQUENCE"

    @property
    def IfExists(self) -> DropSequenceWithIfExists:
        return DropSequenceWithIfExists(self)


DropSequence = DropSequenceKeyword()
