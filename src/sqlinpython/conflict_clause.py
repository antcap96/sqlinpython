from sqlinpython.base import SqlElement


class OnConflict_[T: OnConflictAction](SqlElement):
    def __init__(self, t: type[T], prev: SqlElement):
        self._t = t
        self._prev = prev

    def _create_query(self):
        return f"{self._prev._create_query()} ON CONFLICT"

    @property
    def Rollback(self) -> T:
        return self._t(self, "ROLLBACK")

    @property
    def Abort(self) -> T:
        return self._t(self, "ABORT")

    @property
    def Fail(self) -> T:
        return self._t(self, "FAIL")

    @property
    def Ignore(self) -> T:
        return self._t(self, "IGNORE")

    @property
    def Replace(self) -> T:
        return self._t(self, "REPLACE")


class OnConflictAction(SqlElement):
    def __init__(self, prev: SqlElement, action: str):
        self._prev = prev
        self._action = action

    def _create_query(self):
        return f"{self._prev._create_query()} {self._action}"
