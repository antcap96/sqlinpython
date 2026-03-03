from typing import override

from .core import Expression13


class Literal(Expression13):
    pass


class CurrentTimeKeyword(Literal):
    def __init__(self) -> None:
        pass

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("CURRENT_TIME")


CurrentTime = CurrentTimeKeyword()


class CurrentDateKeyword(Literal):
    def __init__(self) -> None:
        pass

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("CURRENT_DATE")


CurrentDate = CurrentDateKeyword()


class CurrentTimestampKeyword(Literal):
    def __init__(self) -> None:
        pass

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("CURRENT_TIMESTAMP")


CurrentTimestamp = CurrentTimestampKeyword()


class FloatLiteral(Literal):
    def __init__(self, value: float) -> None:
        self._value = value

    # TODO: All this
    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append(str(self._value))


class IntLiteral(Literal):
    def __init__(self, value: int) -> None:
        self._value = value

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append(str(self._value))


class StringLiteral(Literal):
    def __init__(self, value: str) -> None:
        self._value = value

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append(f'"{self._value}"')


class BooleanLiteral(Literal):
    def __init__(self, value: bool) -> None:
        self._value = value

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append(str(self._value).upper())


class NullLiteral(Literal):
    def __init__(self) -> None:
        pass

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append("NULL")


type SqlLiteral = float | str | None | bool


def literal(value: SqlLiteral) -> Literal:
    # The order of bool, int and float is necessary due to the type hierarchy
    if isinstance(value, bool):
        return BooleanLiteral(value)
    elif isinstance(value, int):
        return IntLiteral(value)
    elif isinstance(value, float):
        return FloatLiteral(value)
    elif isinstance(value, str):
        return StringLiteral(value)
    elif value is None:
        return NullLiteral()
    else:
        raise ValueError(f"Unsupported literal type: {type(value)}")
