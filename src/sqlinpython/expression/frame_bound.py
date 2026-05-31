from __future__ import annotations

from abc import ABC
from typing import override

from sqlinpython.base import SqlElement


class FrameBound(SqlElement, ABC):
    pass


class PrecedingFrameBound(FrameBound):
    def __init__(self, expr: SqlElement) -> None:
        self._expr = expr

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._expr._create_query(buffer)
        buffer.append(" PRECEDING")


class FollowingFrameBound(FrameBound):
    def __init__(self, expr: SqlElement) -> None:
        self._expr = expr

    @override
    def _create_query(self, buffer: list[str]) -> None:
        self._expr._create_query(buffer)
        buffer.append(" FOLLOWING")


class IHasFrameBounds(SqlElement, ABC):
    @property
    def Preceding(self) -> PrecedingFrameBound:
        return PrecedingFrameBound(self)

    @property
    def Following(self) -> FollowingFrameBound:
        return FollowingFrameBound(self)
