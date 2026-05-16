from __future__ import annotations

from abc import ABC
from typing import Literal, override

from sqlinpython.base import CompleteSqlQuery, SqlElement


# SPEC: https://sqlite.org/lang_transaction.html
class BeginStatement(CompleteSqlQuery, ABC):
    pass


class BeginWithTransaction(BeginStatement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" TRANSACTION")


class IBeginTransaction(SqlElement, ABC):
    @property
    def Transaction(self) -> BeginWithTransaction:
        return BeginWithTransaction(self)


class BeginWithType(BeginWithTransaction, IBeginTransaction):
    def __init__(
        self,
        prev: SqlElement,
        type_: Literal["DEFERRED", "IMMEDIATE", "EXCLUSIVE"],
    ) -> None:
        self._prev = prev
        self._type = type_

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(f" {self._type}")


class BeginKeyword(BeginWithTransaction, IBeginTransaction):
    def __init__(self) -> None:
        pass

    @property
    def Deferred(self) -> BeginWithType:
        return BeginWithType(self, "DEFERRED")

    @property
    def Immediate(self) -> BeginWithType:
        return BeginWithType(self, "IMMEDIATE")

    @property
    def Exclusive(self) -> BeginWithType:
        return BeginWithType(self, "EXCLUSIVE")

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("BEGIN")


Begin = BeginKeyword()


class CommitStatement(CompleteSqlQuery, ABC):
    pass


class CommitWithTransaction(CommitStatement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" TRANSACTION")


class ICommitTransaction(SqlElement, ABC):
    @property
    def Transaction(self) -> CommitWithTransaction:
        return CommitWithTransaction(self)


class CommitKeyword(CommitWithTransaction, ICommitTransaction):
    def __init__(self) -> None:
        pass

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("COMMIT")


Commit = CommitKeyword()


class EndKeyword(CommitWithTransaction, ICommitTransaction):
    def __init__(self) -> None:
        pass

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("END")


End = EndKeyword()
