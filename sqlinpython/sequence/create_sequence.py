from __future__ import annotations

from abc import ABCMeta
from typing import Literal

from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.create_table import BindParameter
from sqlinpython.expression import Value
from sqlinpython.sequence.core import SequenceRef


class CreateSequenceQuery(CompleteSqlQuery, metaclass=ABCMeta):
    pass


class CreateSequenceWithCache(CreateSequenceQuery):
    def __init__(self, prev: SqlElement, param: Value | BindParameter) -> None:
        self._prev = prev
        self._param = param

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} CACHE {self._param._create_query()}"


class CreateSequenceWithCycle(CreateSequenceWithCache):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} CYCLE"

    def Cache(self, param: Value | BindParameter) -> CreateSequenceWithCache:
        return CreateSequenceWithCache(self, param)


class CreateSequenceWithMaxValue(CreateSequenceWithCycle):
    def __init__(
        self,
        prev: SqlElement,
        param: Value | BindParameter,
    ) -> None:
        self._prev = prev
        self._param = param

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} MAXVALUE {self._param._create_query()}"

    @property
    def Cycle(self) -> CreateSequenceWithCycle:
        return CreateSequenceWithCycle(self)


class CreateSequenceWithMinValue(CreateSequenceWithMaxValue):
    def __init__(
        self,
        prev: SqlElement,
        param: Value | BindParameter,
    ) -> None:
        self._prev = prev
        self._param = param

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} MINVALUE {self._param._create_query()}"

    def MaxValue(self, param: Value | BindParameter) -> CreateSequenceWithMaxValue:
        return CreateSequenceWithMaxValue(self, param)


class CreateSequenceWithIncrement(CreateSequenceWithMinValue):
    def __init__(
        self,
        prev: SqlElement,
        token: Literal["INCREMENT", "INCREMENT BY"],
        param: Value | BindParameter,
    ) -> None:
        self._prev = prev
        self._token = token
        self._param = param

    def _create_query(self) -> str:
        before = f"{self._prev._create_query()} {self._token}"
        return f"{before} {self._param._create_query()}"

    def MinValue(self, param: Value | BindParameter) -> CreateSequenceWithMinValue:
        return CreateSequenceWithMinValue(self, param)


class CreateSequenceWithStart(CreateSequenceWithIncrement):
    def __init__(
        self,
        prev: SqlElement,
        token: Literal["START", "START WITH"],
        param: Value | BindParameter,
    ) -> None:
        self._prev = prev
        self._token = token  # type: ignore
        self._param = param

    def _create_query(self) -> str:
        before = f"{self._prev._create_query()} {self._token}"
        return f"{before} {self._param._create_query()}"

    def Increment(self, param: Value | BindParameter) -> CreateSequenceWithIncrement:
        return CreateSequenceWithIncrement(self, "INCREMENT", param)

    def IncrementBy(self, param: Value | BindParameter) -> CreateSequenceWithIncrement:
        return CreateSequenceWithIncrement(self, "INCREMENT BY", param)


class CreateSequenceWithSequenceRef(CreateSequenceWithStart):
    def __init__(self, prev: SqlElement, sequence_ref: SequenceRef) -> None:
        self._prev = prev
        self._sequence_ref = sequence_ref

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._sequence_ref._create_query()}"

    def Start(self, param: Value | BindParameter) -> CreateSequenceWithStart:
        return CreateSequenceWithStart(self, "START", param)

    def StartWith(self, param: Value | BindParameter) -> CreateSequenceWithStart:
        return CreateSequenceWithStart(self, "START WITH", param)


class CreateSequenceWithIfNotExists(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} IF NOT EXISTS"

    def __call__(self, sequence_ref: SequenceRef) -> CreateSequenceWithSequenceRef:
        return CreateSequenceWithSequenceRef(self, sequence_ref)


class CreateSequenceKeyword(CreateSequenceWithIfNotExists):
    def __init__(self) -> None:
        pass

    def _create_query(self) -> str:
        return f"CREATE SEQUENCE"

    @property
    def IfNotExists(self) -> CreateSequenceWithIfNotExists:
        return CreateSequenceWithIfNotExists(self)


CreateSequence = CreateSequenceKeyword()
