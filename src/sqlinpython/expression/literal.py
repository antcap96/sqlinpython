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
    BeginsWithDigit = enum.auto()
    BeforeDigit = enum.auto()
    AfterDecimalPoint = enum.auto()
    BeginsWithDot = enum.auto()
    DotDigit = enum.auto()
    Exponent = enum.auto()
    ExponentSign = enum.auto()
    ExponentDigit = enum.auto()
    BeginsWith0 = enum.auto()
    BeforeHexdigit = enum.auto()
    AfterHexdigit = enum.auto()


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
                        state = _State.BeginsWith0
                        continue
                    elif _is_digit(c):
                        state = _State.BeginsWithDigit
                        continue
                    elif c == ".":
                        state = _State.BeginsWithDot
                        continue
                    else:
                        raise_message(f"Invalid first character '{c}'")
                case _State.BeginsWith0:
                    if c in "xX":
                        state = _State.BeforeHexdigit
                    elif _is_digit(c):
                        state = _State.BeginsWithDigit
                    elif c == "_":
                        state = _State.BeforeDigit
                    elif c == ".":
                        state = _State.AfterDecimalPoint
                    elif c in "eE":
                        state = _State.Exponent
                    else:
                        raise_message(f"After character after leading 0, got '{c}'")
                case _State.BeforeHexdigit:
                    if _is_hexdigit(c):
                        state = _State.AfterHexdigit
                    else:
                        raise_message(f"Expected hexdigit, got '{c}'")
                case _State.AfterHexdigit:
                    if _is_hexdigit(c):
                        continue
                    if c == "_":
                        state = _State.BeforeHexdigit
                    else:
                        raise_message(f"Expected hexdigit or '_', got '{c}'")
                case _State.BeginsWithDigit:
                    if _is_digit(c):
                        continue
                    if c == "_":
                        state = _State.BeforeDigit
                    elif c == ".":
                        state = _State.AfterDecimalPoint
                    elif c in "eE":
                        state = _State.Exponent
                    else:
                        raise_message(f"Expected digit or '_', got '{c}'")
                case _State.BeforeDigit:
                    if _is_digit(c):
                        state = _State.BeginsWithDigit
                    else:
                        raise_message(f"Expected digit, got '{c}'")
                case _State.BeginsWithDot:
                    if _is_digit(c):
                        state = _State.DotDigit
                    else:
                        raise_message(f"Expected digit, got '{c}'")
                case _State.AfterDecimalPoint:
                    if _is_digit(c):
                        state = _State.DotDigit
                    elif c in "eE":
                        state = _State.Exponent
                    else:
                        raise_message(f"Unexpected character after '.', got '{c}'")
                case _State.DotDigit:
                    if _is_digit(c):
                        continue
                    elif c == "_":
                        state = _State.BeginsWithDot
                    elif c in "eE":
                        state = _State.Exponent
                    else:
                        raise_message(
                            f"Unexpected character in decimal part, got '{c}'"
                        )
                case _State.Exponent:
                    if _is_digit(c):
                        state = _State.ExponentDigit
                    elif c in "+-":
                        state = _State.ExponentSign
                    else:
                        raise_message(f"Unexpected character in exponent, got '{c}'")
                case _State.ExponentSign:
                    if _is_digit(c):
                        state = _State.ExponentDigit
                    else:
                        raise_message(f"Expected digit in exponent, got '{c}'")
                case _State.ExponentDigit:
                    if _is_digit(c):
                        continue
                    elif c == "_":
                        state = _State.ExponentSign
                    else:
                        raise_message(f"Expected digit or '_' in exponent, got '{c}'")

        if state not in (
            _State.AfterDecimalPoint,
            _State.AfterHexdigit,
            _State.BeginsWith0,
            _State.BeginsWithDigit,
            _State.DotDigit,
            _State.ExponentDigit,
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
        raise ValueError(f"Unsupported literal type: {type(value)}")  # pyright: ignore[reportUnreachable]
