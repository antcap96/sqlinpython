from abc import abstractmethod
from typing import Any

from sqlinpython.expression import Term, TermBeforeBracket
from sqlinpython.select_expression import StarKeyword


class Function(TermBeforeBracket):
    @abstractmethod
    def __init__(self, *args: Any) -> None:
        pass

    @abstractmethod
    def _create_query(self) -> str:
        pass


class Avg(Function):
    def __init__(self, numeric_term: Term) -> None:
        self._numeric_term = numeric_term

    def _create_query(self) -> str:
        return f"AVG({self._numeric_term._create_query()})"


class Sum(Function):
    def __init__(self, numeric_term: Term) -> None:
        self._numeric_term = numeric_term

    def _create_query(self) -> str:
        return f"SUM({self._numeric_term._create_query()})"


class Count(Function):
    def __init__(self, term: Term | StarKeyword, *, distinct: bool = False) -> None:
        self._distinct = distinct
        self._term = term

    def _create_query(self) -> str:
        distinct = "DISTINCT " if self._distinct else ""
        return f"COUNT({distinct}{self._term._create_query()})"
