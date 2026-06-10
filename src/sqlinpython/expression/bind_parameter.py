import re
from typing import Literal, overload, override

from sqlinpython.expression.core import Expression12

_TCL_NAME_PATTERN = re.compile(
    r"[A-Za-z_][A-Za-z0-9_]*" + r"(?:::[A-Za-z_][A-Za-z0-9_]*)*" + r"(?:\([^)\s]*\))?"
)


class BindParameter(Expression12):
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, value: int) -> None: ...
    @overload
    def __init__(
        self, value: str, bind_symbol: Literal[":", "$", "@"] = ":"
    ) -> None: ...
    def __init__(
        self, value: int | str | None = None, bind_symbol: Literal[":", "$", "@"] = ":"
    ) -> None:
        self._value = value
        if isinstance(value, int) or value is None:
            self._bind_symbol = "?"
        else:
            if bind_symbol == "$":
                if not _TCL_NAME_PATTERN.fullmatch(value):
                    raise ValueError(
                        f"BindParameter '$' name must match Tcl-style identifier, got {value!r}"
                    )
            elif not value.isalpha():
                raise ValueError(
                    f"BindParameter {bind_symbol!r} name must be alphabetic, got {value!r}"
                )
            self._bind_symbol = bind_symbol

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append(self._bind_symbol)
        if self._value is not None:
            buffer.append(str(self._value))
