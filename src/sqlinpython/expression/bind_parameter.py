from typing import override, Literal, overload

from sqlinpython.expression.core import Expression12


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
            # TODO: Special case for bind_symbol == "$" (https://sqlite.org/lang_expr.html)
            assert value.isalpha()
            self._bind_symbol = bind_symbol

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append(self._bind_symbol)
        if self._value is not None:
            buffer.append(str(self._value))
