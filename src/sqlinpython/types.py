from sqlinpython.type_name import CompleteTypeName, TypeName, TypeNameWithArgs

# SPEC: https://sqlite.org/datatype3.html
#
# Types that never take arguments are constants annotated as CompleteTypeName,
# so calling them is a type error. Types that require arguments are wrapper
# functions, so using them bare is a type error. The raw TypeName builder
# remains the escape hatch for anything else.

# ---------------------------------------------------------------------------
# Cached TypeName instances for the parameterized wrappers (private).
# ---------------------------------------------------------------------------

_CHARACTER = TypeName("CHARACTER")
_VARCHAR = TypeName("VARCHAR")
_VARYING_CHARACTER = TypeName("VARYING", "CHARACTER")
_NCHAR = TypeName("NCHAR")
_NATIVE_CHARACTER = TypeName("NATIVE", "CHARACTER")
_NVARCHAR = TypeName("NVARCHAR")
_DECIMAL = TypeName("DECIMAL")

# ---------------------------------------------------------------------------
# Integer affinity
# ---------------------------------------------------------------------------

Int: CompleteTypeName = TypeName("INT")
Integer: CompleteTypeName = TypeName("INTEGER")
TinyInt: CompleteTypeName = TypeName("TINYINT")
SmallInt: CompleteTypeName = TypeName("SMALLINT")
MediumInt: CompleteTypeName = TypeName("MEDIUMINT")
BigInt: CompleteTypeName = TypeName("BIGINT")
UnsignedBigInt: CompleteTypeName = TypeName("UNSIGNED", "BIG", "INT")
Int2: CompleteTypeName = TypeName("INT2")
Int8: CompleteTypeName = TypeName("INT8")

# ---------------------------------------------------------------------------
# Text affinity
# ---------------------------------------------------------------------------

Text: CompleteTypeName = TypeName("TEXT")
Clob: CompleteTypeName = TypeName("CLOB")


def Character(length: int, /) -> TypeNameWithArgs:
    return _CHARACTER(length)


def Varchar(length: int, /) -> TypeNameWithArgs:
    return _VARCHAR(length)


def VaryingCharacter(length: int, /) -> TypeNameWithArgs:
    return _VARYING_CHARACTER(length)


def Nchar(length: int, /) -> TypeNameWithArgs:
    return _NCHAR(length)


def NativeCharacter(length: int, /) -> TypeNameWithArgs:
    return _NATIVE_CHARACTER(length)


def Nvarchar(length: int, /) -> TypeNameWithArgs:
    return _NVARCHAR(length)


# ---------------------------------------------------------------------------
# Blob affinity
# ---------------------------------------------------------------------------

Blob: CompleteTypeName = TypeName("BLOB")

# ---------------------------------------------------------------------------
# Real affinity
# ---------------------------------------------------------------------------

Real: CompleteTypeName = TypeName("REAL")
Double: CompleteTypeName = TypeName("DOUBLE")
DoublePrecision: CompleteTypeName = TypeName("DOUBLE", "PRECISION")
Float: CompleteTypeName = TypeName("FLOAT")

# ---------------------------------------------------------------------------
# Numeric affinity
# ---------------------------------------------------------------------------

Numeric: CompleteTypeName = TypeName("NUMERIC")
Boolean: CompleteTypeName = TypeName("BOOLEAN")
Date: CompleteTypeName = TypeName("DATE")
Datetime: CompleteTypeName = TypeName("DATETIME")


def Decimal(precision: int, scale: int | None = None, /) -> TypeNameWithArgs:
    return _DECIMAL(precision, scale)


# ---------------------------------------------------------------------------
# STRICT tables
# ---------------------------------------------------------------------------

Any: CompleteTypeName = TypeName("ANY")
