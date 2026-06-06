import enum
from abc import ABC
from typing import NoReturn, override

from .core import Expression13


class Literal(Expression13, ABC):
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


class _State(enum.Enum):
    Start = enum.auto()
    IntZero = enum.auto()
    IntDigit = enum.auto()
    IntExpectDigit = enum.auto()
    FracStart = enum.auto()
    FracExpectDigit = enum.auto()
    FracDigit = enum.auto()
    ExpStart = enum.auto()
    ExpExpectDigit = enum.auto()
    ExpDigit = enum.auto()
    HexExpectDigit = enum.auto()
    HexDigit = enum.auto()


def _is_digit(c: str) -> bool:
    return c.isascii() and c.isdigit()


def _is_hexdigit(c: str) -> bool:
    return _is_digit(c) or c in "ABCDEFabcdef"


class NumericLiteral(Literal):
    """Raw SQLite numeric literal. Underscore separators require SQLite >= 3.46.0."""

    def __init__(self, s: str) -> None:
        state = _State.Start

        def raise_message(err_message: str) -> NoReturn:
            raise ValueError(f"Failed to parse '{s}' as Numeric literal: {err_message}")

        for c in s:
            match state:
                case _State.Start:
                    if c == "0":
                        state = _State.IntZero
                        continue
                    elif _is_digit(c):
                        state = _State.IntDigit
                        continue
                    elif c == ".":
                        state = _State.FracExpectDigit
                        continue
                    else:
                        raise_message(f"Invalid first character '{c}'")
                case _State.IntZero:
                    if c in "xX":
                        state = _State.HexExpectDigit
                    elif _is_digit(c):
                        state = _State.IntDigit
                    elif c == "_":
                        state = _State.IntExpectDigit
                    elif c == ".":
                        state = _State.FracStart
                    elif c in "eE":
                        state = _State.ExpStart
                    else:
                        raise_message(f"After character after leading 0, got '{c}'")
                case _State.HexExpectDigit:
                    if _is_hexdigit(c):
                        state = _State.HexDigit
                    else:
                        raise_message(f"Expected hexdigit, got '{c}'")
                case _State.HexDigit:
                    if _is_hexdigit(c):
                        continue
                    if c == "_":
                        state = _State.HexExpectDigit
                    else:
                        raise_message(f"Expected hexdigit or '_', got '{c}'")
                case _State.IntDigit:
                    if _is_digit(c):
                        continue
                    if c == "_":
                        state = _State.IntExpectDigit
                    elif c == ".":
                        state = _State.FracStart
                    elif c in "eE":
                        state = _State.ExpStart
                    else:
                        raise_message(f"Expected digit or '_', got '{c}'")
                case _State.IntExpectDigit:
                    if _is_digit(c):
                        state = _State.IntDigit
                    else:
                        raise_message(f"Expected digit, got '{c}'")
                case _State.FracExpectDigit:
                    if _is_digit(c):
                        state = _State.FracDigit
                    else:
                        raise_message(f"Expected digit, got '{c}'")
                case _State.FracStart:
                    if _is_digit(c):
                        state = _State.FracDigit
                    elif c in "eE":
                        state = _State.ExpStart
                    else:
                        raise_message(f"Unexpected character after '.', got '{c}'")
                case _State.FracDigit:
                    if _is_digit(c):
                        continue
                    elif c == "_":
                        state = _State.FracExpectDigit
                    elif c in "eE":
                        state = _State.ExpStart
                    else:
                        raise_message(
                            f"Unexpected character in decimal part, got '{c}'"
                        )
                case _State.ExpStart:
                    if _is_digit(c):
                        state = _State.ExpDigit
                    elif c in "+-":
                        state = _State.ExpExpectDigit
                    else:
                        raise_message(f"Unexpected character in exponent, got '{c}'")
                case _State.ExpExpectDigit:
                    if _is_digit(c):
                        state = _State.ExpDigit
                    else:
                        raise_message(f"Expected digit in exponent, got '{c}'")
                case _State.ExpDigit:
                    if _is_digit(c):
                        continue
                    elif c == "_":
                        state = _State.ExpExpectDigit
                    else:
                        raise_message(f"Expected digit or '_' in exponent, got '{c}'")

        if state not in (
            _State.FracStart,
            _State.HexDigit,
            _State.IntZero,
            _State.IntDigit,
            _State.FracDigit,
            _State.ExpDigit,
        ):
            raise_message(f"Invalid terminal State {state}")

        self._s = s

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append(self._s)


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


class HexLiteral(Literal):
    def __init__(self, value: int) -> None:
        if value < 0:
            raise ValueError(f"HexLiteral does not accept negative values, got {value}")
        self._value = value

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append(f"0x{self._value:X}")


class BlobLiteral(Literal):
    def __init__(self, value: bytes) -> None:
        self._value = value

    @override
    def _create_query(self, buffer: list[str]) -> None:
        buffer.append(f"X'{self._value.hex().upper()}'")


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


type SqlLiteral = float | str | bytes | None | bool


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
    elif isinstance(value, bytes):
        return BlobLiteral(value)
    elif value is None:
        return NullLiteral()
    else:
        raise ValueError(f"Unsupported literal type: {type(value)}")  # pyright: ignore[reportUnreachable]
