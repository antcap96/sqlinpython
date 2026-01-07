from abc import ABCMeta, abstractmethod


class SqlElement(metaclass=ABCMeta):
    @abstractmethod
    def _create_query(self) -> str:
        pass


class CompleteSqlQuery(SqlElement, metaclass=ABCMeta):
    def get_query(self) -> str:
        return self._create_query()


class NotImplementedSqlElement(SqlElement):
    def __init__(self, placeholder: str) -> None:
        self._placeholder = placeholder

    def _create_query(self) -> str:
        return self._placeholder
