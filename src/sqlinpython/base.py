import enum
from abc import ABCMeta, abstractmethod
from collections.abc import Iterable
from typing import Protocol


class NoArg(enum.Enum):
    NO_ARG = enum.auto()


class ISqlElement(Protocol):
    def _create_query(self, buffer: list[str]) -> None: ...


def comma_separated(buffer: list[str], elements: Iterable[ISqlElement]) -> None:
    for i, element in enumerate(elements):
        if i > 0:
            buffer.append(", ")
        element._create_query(buffer)


class SqlElement(metaclass=ABCMeta):
    @abstractmethod
    def _create_query(self, buffer: list[str]) -> None:
        pass


class CompleteSqlQuery(SqlElement, metaclass=ABCMeta):
    def get_query(self) -> str:
        buffer: list[str] = []
        self._create_query(buffer)
        return "".join(buffer)
