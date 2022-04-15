from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import Optional


class SqlElement(metaclass=ABCMeta):
    @abstractmethod
    def _create_query(self) -> str:
        pass


class CompleteSqlQuery(SqlElement, metaclass=ABCMeta):
    @abstractmethod
    def get_query(self) -> str:
        pass


class Name(SqlElement):
    def __init__(self, name: str) -> None:
        self._name = name


class ColumnName(Name):
    pass


class ConstrainName(Name):
    def _create_query(self) -> str:
        return self._name


class ColumnNameConstrain(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} ROW TIMESTAMP"


class ColumnNameConstrainRowTimestamp(ColumnNameConstrain):
    def __init__(self, prev: SqlElement, asc: Optional[bool]) -> None:
        self._prev = prev
        self._asc = asc

    @property
    def RowTimestamp(self) -> ColumnNameConstrain:
        return ColumnNameConstrain(self)

    def _create_query(self) -> str:
        s = ""
        match self._asc:
            case True:
                s = " ASC"
            case False:
                s = " DESC"
            case None:
                s = ""
        return f"{self._prev._create_query()}{s}"


class ColumnNameConstrainAscDesc(ColumnNameConstrainRowTimestamp):
    def __init__(self, name: str) -> None:
        self.name = name

    @property
    def Asc(self) -> ColumnNameConstrainRowTimestamp:
        return ColumnNameConstrainRowTimestamp(self, True)

    @property
    def Desc(self) -> ColumnNameConstrainRowTimestamp:
        return ColumnNameConstrainRowTimestamp(self, False)

    def _create_query(self) -> str:
        return self.name


Column = ColumnNameConstrainAscDesc


class Constrain(SqlElement):
    def __call__(self, constrain_name: ConstrainName) -> ConstrainAndName:
        return ConstrainAndName(self, constrain_name)

    def _create_query(self) -> str:
        return "CONSTRAIN"


class ConstrainAndName(SqlElement):
    def __init__(self, prev: SqlElement, constrain_name: ConstrainName) -> None:
        self._prev = prev
        self._constrain_name = constrain_name

    @property
    def PrimaryKey(self) -> ConstrainBeginnig:
        return ConstrainBeginnig(self)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} {self._constrain_name._name}"


class ConstrainBeginnig(SqlElement):
    def __init__(self, prev: SqlElement):
        self._prev = prev

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} PRIMARY KEY"

    def __call__(
        self, first_column_name: ColumnNameConstrain, *column_names: ColumnNameConstrain
    ) -> ConstrainQuery:
        return ConstrainQuery(self, (first_column_name, *column_names))


class ConstrainQuery(CompleteSqlQuery):
    def __init__(
        self, prev: SqlElement, column_names: tuple[ColumnNameConstrain, ...]
    ) -> None:
        self._prev = prev
        self._column_names = column_names

    def _create_query(self) -> str:
        col_name_queries = [col_name._create_query() for col_name in self._column_names]
        col_name_query = ", ".join(col_name_queries)
        return f"{self._prev._create_query()}({col_name_query})"

    def get_query(self) -> str:
        return self._create_query()


constrain = Constrain()

if __name__ == "__main__":
    print(
        constrain(ConstrainName("test"))
        .PrimaryKey(
            Column("test1"), Column("test2").Asc, Column("test3").Desc.RowTimestamp
        )
        .get_query()
    )
