from abc import ABCMeta, abstractmethod


class SqlElement(metaclass=ABCMeta):
    @abstractmethod
    def _create_query(self, buffer: list[str]) -> None:
        pass


class CompleteSqlQuery(SqlElement, metaclass=ABCMeta):
    def get_query(self) -> str:
        buffer: list[str] = []
        self._create_query(buffer)
        return "".join(buffer)


class NotImplementedSqlElement(SqlElement):
    def __init__(self, placeholder: str) -> None:
        self._placeholder = placeholder

    def _create_query(self, buffer: list[str]) -> None:
        buffer.append(self._placeholder)
