from __future__ import annotations

from typing import Optional

from sqlinpython.base import SqlElement


class DataType(SqlElement):
    pass


class DataTypeWithType(DataType):
    @property
    def Array(self) -> DataTypeWithArray:
        return DataTypeWithArray(self)


class DataTypeWithArray(DataType):
    def __init__(self, prev: SqlElement) -> None:
        self._prev = prev

    def __getitem__(self, dimension: Optional[int] = None) -> DataTypeWithBrackets:
        return DataTypeWithBrackets(self, dimension)

    def _create_query(self) -> str:
        return f"{self._prev._create_query()} ARRAY"


class DataTypeWithBrackets(DataType):
    def __init__(self, prev: SqlElement, dimension: Optional[int]) -> None:
        self._prev = prev
        self._dimension = dimension

    def _create_query(self) -> str:
        dim = "" if self._dimension is None else str(self._dimension)
        return f"{self._prev._create_query()}[{dim}]"


# CHAR
class CharType:
    def __call__(self, precision: int) -> CharTypeWithPrecision:
        return CharTypeWithPrecision(precision)


class CharTypeWithPrecision(DataTypeWithType):
    def __init__(self, precision: int) -> None:
        self._precision = precision

    def _create_query(self) -> str:
        return f"CHAR({self._precision})"


# VARCHAR
class VarcharType(DataTypeWithType):
    def __call__(self, precision: int) -> VarcharTypeWithPrecision:
        return VarcharTypeWithPrecision(precision)

    def _create_query(self) -> str:
        return f"VARCHAR"


class VarcharTypeWithPrecision(DataTypeWithType):
    def __init__(self, precision: int) -> None:
        self._precision = precision

    def _create_query(self) -> str:
        return f"VARCHAR({self._precision})"


# DECIMAL
class DecimalType(DataTypeWithType):
    def __call__(self, precision: int, scale: int) -> DecimalTypeWithPrecision:
        return DecimalTypeWithPrecision(precision, scale)

    def _create_query(self) -> str:
        return f"DECIMAL"


class DecimalTypeWithPrecision(DataTypeWithType):
    def __init__(self, precision: int, scale: int) -> None:
        self._precision = precision
        self._scale = scale

    def _create_query(self) -> str:
        return f"DECIMAL({self._precision}, {self._scale})"


# TINYINT
class TinyintType(DataTypeWithType):
    def _create_query(self) -> str:
        return f"TINYINT"


# SMALLINT
class SmallintType(DataTypeWithType):
    def _create_query(self) -> str:
        return f"SMALLINT"


# INTEGER
class IntegerType(DataTypeWithType):
    def _create_query(self) -> str:
        return f"INTEGER"


# BIGINT
class BigintType(DataTypeWithType):
    def _create_query(self) -> str:
        return f"BIGINT"


# FLOAT
class FloatType(DataTypeWithType):
    def _create_query(self) -> str:
        return f"FLOAT"


# DOUBLE
class DoubleType(DataTypeWithType):
    def _create_query(self) -> str:
        return f"DOUBLE"


# TIMESTAMP
class TimestampType(DataTypeWithType):
    def _create_query(self) -> str:
        return f"TIMESTAMP"


# DATE
class DateType(DataTypeWithType):
    def _create_query(self) -> str:
        return f"DATE"


# TIME
class TimeType(DataTypeWithType):
    def _create_query(self) -> str:
        return f"TIME"


# BINARY
class BinaryType(DataTypeWithType):
    def __call__(self, precision: int) -> BinaryTypeWithPrecision:
        return BinaryTypeWithPrecision(precision)

    def _create_query(self) -> str:
        return f"BINARY"


class BinaryTypeWithPrecision(DataTypeWithType):
    def __init__(self, precision: int) -> None:
        self._precision = precision

    def _create_query(self) -> str:
        return f"BINARY({self._precision})"


# VARBINARY
class VarbinaryType(DataTypeWithType):
    def _create_query(self) -> str:
        return f"VARBINARY"


Char = CharType()
Varchar = VarcharType()
Decimal = DecimalType()
Tinyint = TinyintType()
Smallint = SmallintType()
Integer = IntegerType()
Bigint = BigintType()
Float = FloatType()
Double = DoubleType()
Timestamp = TimestampType()
Date = DateType()
Time = TimeType()
Binary = BinaryType()
Varbinary = VarbinaryType()
