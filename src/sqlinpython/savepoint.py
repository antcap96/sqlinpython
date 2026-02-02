from sqlinpython.base import CompleteSqlQuery, SqlElement
from sqlinpython.name import Name

# TODO: Consider a SavepointName


class SavepointComplete(CompleteSqlQuery):
    def __init__(self, prev: SqlElement, savepoint: Name) -> None:
        self._prev = prev
        self._savepoint = savepoint

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._savepoint._create_query(buffer)


class SavepointKeyword(SqlElement):
    def __init__(self) -> None:
        pass

    def __call__(self, savepoint: Name | str) -> SavepointComplete:
        if isinstance(savepoint, str):
            savepoint = Name(savepoint)
        return SavepointComplete(self, savepoint)

    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("SAVEPOINT")


Savepoint = SavepointKeyword()


class ReleaseComplete(CompleteSqlQuery):
    def __init__(self, prev: SqlElement, savepoint: Name) -> None:
        self._prev = prev
        self._savepoint = savepoint

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._savepoint._create_query(buffer)


class ReleaseWithSavepoint(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def __call__(self, savepoint: Name | str) -> ReleaseComplete:
        if isinstance(savepoint, str):
            savepoint = Name(savepoint)
        return ReleaseComplete(self, savepoint)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" SAVEPOINT")


class ReleaseKeyword(ReleaseWithSavepoint):
    def __init__(self) -> None:
        pass

    @property
    def Savepoint(self) -> ReleaseWithSavepoint:
        return ReleaseWithSavepoint(self)

    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("RELEASE")


Release = ReleaseKeyword()


class RollbackComplete(CompleteSqlQuery):
    def __init__(self, prev: SqlElement, savepoint: Name) -> None:
        self._prev = prev
        self._savepoint = savepoint

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" ")
        self._savepoint._create_query(buffer)


class RollbackWithToSavepoint(SqlElement):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def __call__(self, savepoint: Name | str) -> RollbackComplete:
        if isinstance(savepoint, str):
            savepoint = Name(savepoint)
        return RollbackComplete(self, savepoint)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" SAVEPOINT")


class RollbackWithTo(RollbackWithToSavepoint):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def Savepoint(self) -> RollbackWithToSavepoint:
        return RollbackWithToSavepoint(self)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" TO")


class RollbackWithTransaction(RollbackComplete):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    @property
    def To(self) -> RollbackWithTo:
        return RollbackWithTo(self)

    def _create_query(self, buffer: list[str]) -> None:
        self._prev._create_query(buffer)
        buffer.append(" TRANSACTION")


class RollbackKeyword(RollbackWithTransaction):
    def __init__(self) -> None:
        pass

    @property
    def Transaction(self) -> RollbackWithTransaction:
        return RollbackWithTransaction(self)

    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("ROLLBACK")


Rollback = RollbackKeyword()
