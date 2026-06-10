from typing import Literal, overload

from sqlinpython.expression import (
    ExpressionOrLiteral,
    FunctionCall,
    FunctionName,
    Star_,
)
from sqlinpython.ordering_term import OrderingTerm

# ---------------------------------------------------------------------------
# Cached FunctionName instances (private). One per SQL function name.
# ---------------------------------------------------------------------------

# Aggregate
_AVG = FunctionName("AVG")
_COUNT = FunctionName("COUNT")
_GROUP_CONCAT = FunctionName("GROUP_CONCAT")
_MAX = FunctionName("MAX")
_MEDIAN = FunctionName("MEDIAN")
_MIN = FunctionName("MIN")
_PERCENTILE = FunctionName("PERCENTILE")
_PERCENTILE_CONT = FunctionName("PERCENTILE_CONT")
_PERCENTILE_DISC = FunctionName("PERCENTILE_DISC")
_STRING_AGG = FunctionName("STRING_AGG")
_SUM = FunctionName("SUM")
_TOTAL = FunctionName("TOTAL")

# Conditional
_COALESCE = FunctionName("COALESCE")
_IF = FunctionName("IF")
_IIF = FunctionName("IIF")
_IFNULL = FunctionName("IFNULL")
_NULLIF = FunctionName("NULLIF")

# String
_CHAR = FunctionName("CHAR")
_CONCAT = FunctionName("CONCAT")
_CONCAT_WS = FunctionName("CONCAT_WS")
_FORMAT = FunctionName("FORMAT")
_GLOB = FunctionName("GLOB")
_INSTR = FunctionName("INSTR")
_LENGTH = FunctionName("LENGTH")
_LIKE = FunctionName("LIKE")
_LOWER = FunctionName("LOWER")
_LTRIM = FunctionName("LTRIM")
_OCTET_LENGTH = FunctionName("OCTET_LENGTH")
_PRINTF = FunctionName("PRINTF")
_QUOTE = FunctionName("QUOTE")
_REPLACE = FunctionName("REPLACE")
_RTRIM = FunctionName("RTRIM")
_SOUNDEX = FunctionName("SOUNDEX")
_SUBSTR = FunctionName("SUBSTR")
_SUBSTRING = FunctionName("SUBSTRING")
_TRIM = FunctionName("TRIM")
_UNICODE = FunctionName("UNICODE")
_UNISTR = FunctionName("UNISTR")
_UNISTR_QUOTE = FunctionName("UNISTR_QUOTE")
_UPPER = FunctionName("UPPER")

# Numeric
_ABS = FunctionName("ABS")
_ACOS = FunctionName("ACOS")
_ACOSH = FunctionName("ACOSH")
_ASIN = FunctionName("ASIN")
_ASINH = FunctionName("ASINH")
_ATAN = FunctionName("ATAN")
_ATAN2 = FunctionName("ATAN2")
_ATANH = FunctionName("ATANH")
_CEIL = FunctionName("CEIL")
_CEILING = FunctionName("CEILING")
_COS = FunctionName("COS")
_COSH = FunctionName("COSH")
_DEGREES = FunctionName("DEGREES")
_EXP = FunctionName("EXP")
_FLOOR = FunctionName("FLOOR")
_LN = FunctionName("LN")
_LOG = FunctionName("LOG")
_LOG10 = FunctionName("LOG10")
_LOG2 = FunctionName("LOG2")
_MOD = FunctionName("MOD")
_PI = FunctionName("PI")
_POW = FunctionName("POW")
_POWER = FunctionName("POWER")
_RADIANS = FunctionName("RADIANS")
_RANDOM = FunctionName("RANDOM")
_ROUND = FunctionName("ROUND")
_SIGN = FunctionName("SIGN")
_SIN = FunctionName("SIN")
_SINH = FunctionName("SINH")
_SQRT = FunctionName("SQRT")
_TAN = FunctionName("TAN")
_TANH = FunctionName("TANH")
_TRUNC = FunctionName("TRUNC")

# Blob / hex
_HEX = FunctionName("HEX")
_RANDOMBLOB = FunctionName("RANDOMBLOB")
_UNHEX = FunctionName("UNHEX")
_ZEROBLOB = FunctionName("ZEROBLOB")

# Type / optimizer hints
_LIKELIHOOD = FunctionName("LIKELIHOOD")
_LIKELY = FunctionName("LIKELY")
_TYPEOF = FunctionName("TYPEOF")
_UNLIKELY = FunctionName("UNLIKELY")

# Connection / metadata
_CHANGES = FunctionName("CHANGES")
_LAST_INSERT_ROWID = FunctionName("LAST_INSERT_ROWID")
_LOAD_EXTENSION = FunctionName("LOAD_EXTENSION")
_SQLITE_COMPILEOPTION_GET = FunctionName("SQLITE_COMPILEOPTION_GET")
_SQLITE_COMPILEOPTION_USED = FunctionName("SQLITE_COMPILEOPTION_USED")
_SQLITE_OFFSET = FunctionName("SQLITE_OFFSET")
_SQLITE_SOURCE_ID = FunctionName("SQLITE_SOURCE_ID")
_SQLITE_VERSION = FunctionName("SQLITE_VERSION")
_TOTAL_CHANGES = FunctionName("TOTAL_CHANGES")

# Date / time
_DATE = FunctionName("DATE")
_DATETIME = FunctionName("DATETIME")
_JULIANDAY = FunctionName("JULIANDAY")
_STRFTIME = FunctionName("STRFTIME")
_TIME = FunctionName("TIME")
_TIMEDIFF = FunctionName("TIMEDIFF")
_UNIXEPOCH = FunctionName("UNIXEPOCH")

# Window
_CUME_DIST = FunctionName("CUME_DIST")
_DENSE_RANK = FunctionName("DENSE_RANK")
_FIRST_VALUE = FunctionName("FIRST_VALUE")
_LAG = FunctionName("LAG")
_LAST_VALUE = FunctionName("LAST_VALUE")
_LEAD = FunctionName("LEAD")
_NTH_VALUE = FunctionName("NTH_VALUE")
_NTILE = FunctionName("NTILE")
_PERCENT_RANK = FunctionName("PERCENT_RANK")
_RANK = FunctionName("RANK")
_ROW_NUMBER = FunctionName("ROW_NUMBER")

# JSON1 scalar
_JSON = FunctionName("JSON")
_JSONB = FunctionName("JSONB")
_JSON_ARRAY = FunctionName("JSON_ARRAY")
_JSONB_ARRAY = FunctionName("JSONB_ARRAY")
_JSON_ARRAY_INSERT = FunctionName("JSON_ARRAY_INSERT")
_JSONB_ARRAY_INSERT = FunctionName("JSONB_ARRAY_INSERT")
_JSON_ARRAY_LENGTH = FunctionName("JSON_ARRAY_LENGTH")
_JSON_ERROR_POSITION = FunctionName("JSON_ERROR_POSITION")
_JSON_EXTRACT = FunctionName("JSON_EXTRACT")
_JSONB_EXTRACT = FunctionName("JSONB_EXTRACT")
_JSON_INSERT = FunctionName("JSON_INSERT")
_JSONB_INSERT = FunctionName("JSONB_INSERT")
_JSON_OBJECT = FunctionName("JSON_OBJECT")
_JSONB_OBJECT = FunctionName("JSONB_OBJECT")
_JSON_PATCH = FunctionName("JSON_PATCH")
_JSONB_PATCH = FunctionName("JSONB_PATCH")
_JSON_PRETTY = FunctionName("JSON_PRETTY")
_JSON_QUOTE = FunctionName("JSON_QUOTE")
_JSON_REMOVE = FunctionName("JSON_REMOVE")
_JSONB_REMOVE = FunctionName("JSONB_REMOVE")
_JSON_REPLACE = FunctionName("JSON_REPLACE")
_JSONB_REPLACE = FunctionName("JSONB_REPLACE")
_JSON_SET = FunctionName("JSON_SET")
_JSONB_SET = FunctionName("JSONB_SET")
_JSON_TYPE = FunctionName("JSON_TYPE")
_JSON_VALID = FunctionName("JSON_VALID")

# JSON1 aggregate
_JSON_GROUP_ARRAY = FunctionName("JSON_GROUP_ARRAY")
_JSONB_GROUP_ARRAY = FunctionName("JSONB_GROUP_ARRAY")
_JSON_GROUP_OBJECT = FunctionName("JSON_GROUP_OBJECT")
_JSONB_GROUP_OBJECT = FunctionName("JSONB_GROUP_OBJECT")


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------


def Avg(
    x: ExpressionOrLiteral,
    /,
    *,
    distinct: bool = False,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall:
    return _AVG(x, distinct=distinct, order_by=order_by)


@overload
def Count(x: Literal["*"] | Star_, /) -> FunctionCall: ...
@overload
def Count(
    x: ExpressionOrLiteral,
    /,
    *,
    distinct: bool = False,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall: ...
def Count(
    x: Literal["*"] | Star_ | ExpressionOrLiteral,
    /,
    *,
    distinct: bool = False,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall:
    if x == "*" or isinstance(x, Star_):
        return _COUNT(x)
    return _COUNT(x, distinct=distinct, order_by=order_by)


@overload
def GroupConcat(
    x: ExpressionOrLiteral,
    /,
    *,
    distinct: bool = False,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall: ...
@overload
def GroupConcat(
    x: ExpressionOrLiteral,
    sep: ExpressionOrLiteral,
    /,
    *,
    distinct: bool = False,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall: ...
def GroupConcat(
    *args: ExpressionOrLiteral,
    distinct: bool = False,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall:
    return _GROUP_CONCAT(*args, distinct=distinct, order_by=order_by)


@overload
def Max(
    x: ExpressionOrLiteral,
    /,
    *,
    distinct: bool = False,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall: ...
@overload
def Max(
    x: ExpressionOrLiteral,
    y: ExpressionOrLiteral,
    /,
    *rest: ExpressionOrLiteral,
) -> FunctionCall: ...
def Max(
    *args: ExpressionOrLiteral,
    distinct: bool = False,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall:
    return _MAX(*args, distinct=distinct, order_by=order_by)


def Median(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _MEDIAN(x)


@overload
def Min(
    x: ExpressionOrLiteral,
    /,
    *,
    distinct: bool = False,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall: ...
@overload
def Min(
    x: ExpressionOrLiteral,
    y: ExpressionOrLiteral,
    /,
    *rest: ExpressionOrLiteral,
) -> FunctionCall: ...
def Min(
    *args: ExpressionOrLiteral,
    distinct: bool = False,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall:
    return _MIN(*args, distinct=distinct, order_by=order_by)


def Percentile(
    y: ExpressionOrLiteral,
    p: ExpressionOrLiteral,
    /,
    *,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall:
    return _PERCENTILE(y, p, order_by=order_by)


def PercentileCont(
    y: ExpressionOrLiteral,
    p: ExpressionOrLiteral,
    /,
    *,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall:
    return _PERCENTILE_CONT(y, p, order_by=order_by)


def PercentileDisc(
    y: ExpressionOrLiteral,
    p: ExpressionOrLiteral,
    /,
    *,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall:
    return _PERCENTILE_DISC(y, p, order_by=order_by)


def StringAgg(
    x: ExpressionOrLiteral,
    sep: ExpressionOrLiteral,
    /,
    *,
    distinct: bool = False,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall:
    return _STRING_AGG(x, sep, distinct=distinct, order_by=order_by)


def Sum(
    x: ExpressionOrLiteral,
    /,
    *,
    distinct: bool = False,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall:
    return _SUM(x, distinct=distinct, order_by=order_by)


def Total(
    x: ExpressionOrLiteral,
    /,
    *,
    distinct: bool = False,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall:
    return _TOTAL(x, distinct=distinct, order_by=order_by)


# ---------------------------------------------------------------------------
# Conditional
# ---------------------------------------------------------------------------


def Coalesce(
    *args: *tuple[
        ExpressionOrLiteral, ExpressionOrLiteral, *tuple[ExpressionOrLiteral, ...]
    ],
) -> FunctionCall:
    return _COALESCE(*args)


def If(
    *args: *tuple[
        ExpressionOrLiteral, ExpressionOrLiteral, *tuple[ExpressionOrLiteral, ...]
    ],
) -> FunctionCall:
    return _IF(*args)


def Iif(
    *args: *tuple[
        ExpressionOrLiteral, ExpressionOrLiteral, *tuple[ExpressionOrLiteral, ...]
    ],
) -> FunctionCall:
    return _IIF(*args)


def Ifnull(x: ExpressionOrLiteral, y: ExpressionOrLiteral, /) -> FunctionCall:
    return _IFNULL(x, y)


def Nullif(x: ExpressionOrLiteral, y: ExpressionOrLiteral, /) -> FunctionCall:
    return _NULLIF(x, y)


# ---------------------------------------------------------------------------
# String
# ---------------------------------------------------------------------------


def Char(
    *args: *tuple[ExpressionOrLiteral, *tuple[ExpressionOrLiteral, ...]],
) -> FunctionCall:
    return _CHAR(*args)


def Concat(
    *args: *tuple[ExpressionOrLiteral, *tuple[ExpressionOrLiteral, ...]],
) -> FunctionCall:
    return _CONCAT(*args)


def ConcatWs(
    *args: *tuple[
        ExpressionOrLiteral, ExpressionOrLiteral, *tuple[ExpressionOrLiteral, ...]
    ],
) -> FunctionCall:
    return _CONCAT_WS(*args)


def Format(
    *args: *tuple[ExpressionOrLiteral, *tuple[ExpressionOrLiteral, ...]],
) -> FunctionCall:
    return _FORMAT(*args)


def Glob(x: ExpressionOrLiteral, y: ExpressionOrLiteral, /) -> FunctionCall:
    return _GLOB(x, y)


def Instr(x: ExpressionOrLiteral, y: ExpressionOrLiteral, /) -> FunctionCall:
    return _INSTR(x, y)


def Length(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _LENGTH(x)


@overload
def Like(x: ExpressionOrLiteral, y: ExpressionOrLiteral, /) -> FunctionCall: ...
@overload
def Like(
    x: ExpressionOrLiteral,
    y: ExpressionOrLiteral,
    escape: ExpressionOrLiteral,
    /,
) -> FunctionCall: ...
def Like(*args: ExpressionOrLiteral) -> FunctionCall:
    return _LIKE(*args)


def Lower(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _LOWER(x)


@overload
def Ltrim(x: ExpressionOrLiteral, /) -> FunctionCall: ...
@overload
def Ltrim(x: ExpressionOrLiteral, y: ExpressionOrLiteral, /) -> FunctionCall: ...
def Ltrim(*args: ExpressionOrLiteral) -> FunctionCall:
    return _LTRIM(*args)


def OctetLength(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _OCTET_LENGTH(x)


def Printf(
    *args: *tuple[ExpressionOrLiteral, *tuple[ExpressionOrLiteral, ...]],
) -> FunctionCall:
    return _PRINTF(*args)


def Quote(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _QUOTE(x)


def Replace(
    x: ExpressionOrLiteral,
    y: ExpressionOrLiteral,
    z: ExpressionOrLiteral,
    /,
) -> FunctionCall:
    return _REPLACE(x, y, z)


@overload
def Rtrim(x: ExpressionOrLiteral, /) -> FunctionCall: ...
@overload
def Rtrim(x: ExpressionOrLiteral, y: ExpressionOrLiteral, /) -> FunctionCall: ...
def Rtrim(*args: ExpressionOrLiteral) -> FunctionCall:
    return _RTRIM(*args)


def Soundex(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _SOUNDEX(x)


@overload
def Substr(x: ExpressionOrLiteral, y: ExpressionOrLiteral, /) -> FunctionCall: ...
@overload
def Substr(
    x: ExpressionOrLiteral,
    y: ExpressionOrLiteral,
    z: ExpressionOrLiteral,
    /,
) -> FunctionCall: ...
def Substr(*args: ExpressionOrLiteral) -> FunctionCall:
    return _SUBSTR(*args)


@overload
def Substring(x: ExpressionOrLiteral, y: ExpressionOrLiteral, /) -> FunctionCall: ...
@overload
def Substring(
    x: ExpressionOrLiteral,
    y: ExpressionOrLiteral,
    z: ExpressionOrLiteral,
    /,
) -> FunctionCall: ...
def Substring(*args: ExpressionOrLiteral) -> FunctionCall:
    return _SUBSTRING(*args)


@overload
def Trim(x: ExpressionOrLiteral, /) -> FunctionCall: ...
@overload
def Trim(x: ExpressionOrLiteral, y: ExpressionOrLiteral, /) -> FunctionCall: ...
def Trim(*args: ExpressionOrLiteral) -> FunctionCall:
    return _TRIM(*args)


def Unicode(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _UNICODE(x)


def Unistr(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _UNISTR(x)


def UnistrQuote(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _UNISTR_QUOTE(x)


def Upper(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _UPPER(x)


# ---------------------------------------------------------------------------
# Numeric
# ---------------------------------------------------------------------------


def Abs(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _ABS(x)


def Acos(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _ACOS(x)


def Acosh(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _ACOSH(x)


def Asin(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _ASIN(x)


def Asinh(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _ASINH(x)


def Atan(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _ATAN(x)


def Atan2(y: ExpressionOrLiteral, x: ExpressionOrLiteral, /) -> FunctionCall:
    return _ATAN2(y, x)


def Atanh(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _ATANH(x)


def Ceil(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _CEIL(x)


def Ceiling(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _CEILING(x)


def Cos(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _COS(x)


def Cosh(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _COSH(x)


def Degrees(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _DEGREES(x)


def Exp(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _EXP(x)


def Floor(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _FLOOR(x)


def Ln(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _LN(x)


@overload
def Log(x: ExpressionOrLiteral, /) -> FunctionCall: ...
@overload
def Log(b: ExpressionOrLiteral, x: ExpressionOrLiteral, /) -> FunctionCall: ...
def Log(*args: ExpressionOrLiteral) -> FunctionCall:
    return _LOG(*args)


def Log10(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _LOG10(x)


def Log2(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _LOG2(x)


def Mod(x: ExpressionOrLiteral, y: ExpressionOrLiteral, /) -> FunctionCall:
    return _MOD(x, y)


def Pi() -> FunctionCall:
    return _PI()


def Pow(x: ExpressionOrLiteral, y: ExpressionOrLiteral, /) -> FunctionCall:
    return _POW(x, y)


def Power(x: ExpressionOrLiteral, y: ExpressionOrLiteral, /) -> FunctionCall:
    return _POWER(x, y)


def Radians(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _RADIANS(x)


def Random() -> FunctionCall:
    return _RANDOM()


@overload
def Round(x: ExpressionOrLiteral, /) -> FunctionCall: ...
@overload
def Round(x: ExpressionOrLiteral, y: ExpressionOrLiteral, /) -> FunctionCall: ...
def Round(*args: ExpressionOrLiteral) -> FunctionCall:
    return _ROUND(*args)


def Sign(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _SIGN(x)


def Sin(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _SIN(x)


def Sinh(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _SINH(x)


def Sqrt(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _SQRT(x)


def Tan(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _TAN(x)


def Tanh(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _TANH(x)


def Trunc(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _TRUNC(x)


# ---------------------------------------------------------------------------
# Blob / hex
# ---------------------------------------------------------------------------


def Hex(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _HEX(x)


def Randomblob(n: ExpressionOrLiteral, /) -> FunctionCall:
    return _RANDOMBLOB(n)


@overload
def Unhex(x: ExpressionOrLiteral, /) -> FunctionCall: ...
@overload
def Unhex(x: ExpressionOrLiteral, y: ExpressionOrLiteral, /) -> FunctionCall: ...
def Unhex(*args: ExpressionOrLiteral) -> FunctionCall:
    return _UNHEX(*args)


def Zeroblob(n: ExpressionOrLiteral, /) -> FunctionCall:
    return _ZEROBLOB(n)


# ---------------------------------------------------------------------------
# Type / optimizer hints
# ---------------------------------------------------------------------------


def Likelihood(x: ExpressionOrLiteral, y: ExpressionOrLiteral, /) -> FunctionCall:
    return _LIKELIHOOD(x, y)


def Likely(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _LIKELY(x)


def Typeof(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _TYPEOF(x)


def Unlikely(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _UNLIKELY(x)


# ---------------------------------------------------------------------------
# Connection / metadata
# ---------------------------------------------------------------------------


def Changes() -> FunctionCall:
    return _CHANGES()


def LastInsertRowid() -> FunctionCall:
    return _LAST_INSERT_ROWID()


@overload
def LoadExtension(x: ExpressionOrLiteral, /) -> FunctionCall: ...
@overload
def LoadExtension(
    x: ExpressionOrLiteral, y: ExpressionOrLiteral, /
) -> FunctionCall: ...
def LoadExtension(*args: ExpressionOrLiteral) -> FunctionCall:
    return _LOAD_EXTENSION(*args)


def SqliteCompileoptionGet(n: ExpressionOrLiteral, /) -> FunctionCall:
    return _SQLITE_COMPILEOPTION_GET(n)


def SqliteCompileoptionUsed(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _SQLITE_COMPILEOPTION_USED(x)


def SqliteOffset(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _SQLITE_OFFSET(x)


def SqliteSourceId() -> FunctionCall:
    return _SQLITE_SOURCE_ID()


def SqliteVersion() -> FunctionCall:
    return _SQLITE_VERSION()


def TotalChanges() -> FunctionCall:
    return _TOTAL_CHANGES()


# ---------------------------------------------------------------------------
# Date / time
# ---------------------------------------------------------------------------


def Date(*args: ExpressionOrLiteral) -> FunctionCall:
    return _DATE(*args)


def Datetime(*args: ExpressionOrLiteral) -> FunctionCall:
    return _DATETIME(*args)


def Julianday(*args: ExpressionOrLiteral) -> FunctionCall:
    return _JULIANDAY(*args)


def Strftime(
    *args: *tuple[
        ExpressionOrLiteral, ExpressionOrLiteral, *tuple[ExpressionOrLiteral, ...]
    ],
) -> FunctionCall:
    return _STRFTIME(*args)


def Time(*args: ExpressionOrLiteral) -> FunctionCall:
    return _TIME(*args)


def Timediff(time1: ExpressionOrLiteral, time2: ExpressionOrLiteral, /) -> FunctionCall:
    return _TIMEDIFF(time1, time2)


def Unixepoch(*args: ExpressionOrLiteral) -> FunctionCall:
    return _UNIXEPOCH(*args)


# ---------------------------------------------------------------------------
# Window
# ---------------------------------------------------------------------------


def CumeDist() -> FunctionCall:
    return _CUME_DIST()


def DenseRank() -> FunctionCall:
    return _DENSE_RANK()


def FirstValue(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _FIRST_VALUE(x)


@overload
def Lag(x: ExpressionOrLiteral, /) -> FunctionCall: ...
@overload
def Lag(x: ExpressionOrLiteral, y: ExpressionOrLiteral, /) -> FunctionCall: ...
@overload
def Lag(
    x: ExpressionOrLiteral,
    y: ExpressionOrLiteral,
    z: ExpressionOrLiteral,
    /,
) -> FunctionCall: ...
def Lag(*args: ExpressionOrLiteral) -> FunctionCall:
    return _LAG(*args)


def LastValue(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _LAST_VALUE(x)


@overload
def Lead(x: ExpressionOrLiteral, /) -> FunctionCall: ...
@overload
def Lead(x: ExpressionOrLiteral, y: ExpressionOrLiteral, /) -> FunctionCall: ...
@overload
def Lead(
    x: ExpressionOrLiteral,
    y: ExpressionOrLiteral,
    z: ExpressionOrLiteral,
    /,
) -> FunctionCall: ...
def Lead(*args: ExpressionOrLiteral) -> FunctionCall:
    return _LEAD(*args)


def NthValue(x: ExpressionOrLiteral, n: ExpressionOrLiteral, /) -> FunctionCall:
    return _NTH_VALUE(x, n)


def Ntile(n: ExpressionOrLiteral, /) -> FunctionCall:
    return _NTILE(n)


def PercentRank() -> FunctionCall:
    return _PERCENT_RANK()


def Rank() -> FunctionCall:
    return _RANK()


def RowNumber() -> FunctionCall:
    return _ROW_NUMBER()


# ---------------------------------------------------------------------------
# JSON1 scalar
# ---------------------------------------------------------------------------


def Json(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _JSON(x)


def Jsonb(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _JSONB(x)


def JsonArray(*args: ExpressionOrLiteral) -> FunctionCall:
    return _JSON_ARRAY(*args)


def JsonbArray(*args: ExpressionOrLiteral) -> FunctionCall:
    return _JSONB_ARRAY(*args)


def JsonArrayInsert(
    *args: *tuple[
        ExpressionOrLiteral,
        ExpressionOrLiteral,
        ExpressionOrLiteral,
        *tuple[ExpressionOrLiteral, ...],
    ],
) -> FunctionCall:
    return _JSON_ARRAY_INSERT(*args)


def JsonbArrayInsert(
    *args: *tuple[
        ExpressionOrLiteral,
        ExpressionOrLiteral,
        ExpressionOrLiteral,
        *tuple[ExpressionOrLiteral, ...],
    ],
) -> FunctionCall:
    return _JSONB_ARRAY_INSERT(*args)


@overload
def JsonArrayLength(x: ExpressionOrLiteral, /) -> FunctionCall: ...
@overload
def JsonArrayLength(
    x: ExpressionOrLiteral, path: ExpressionOrLiteral, /
) -> FunctionCall: ...
def JsonArrayLength(*args: ExpressionOrLiteral) -> FunctionCall:
    return _JSON_ARRAY_LENGTH(*args)


def JsonErrorPosition(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _JSON_ERROR_POSITION(x)


def JsonExtract(
    *args: *tuple[
        ExpressionOrLiteral, ExpressionOrLiteral, *tuple[ExpressionOrLiteral, ...]
    ],
) -> FunctionCall:
    return _JSON_EXTRACT(*args)


def JsonbExtract(
    *args: *tuple[
        ExpressionOrLiteral, ExpressionOrLiteral, *tuple[ExpressionOrLiteral, ...]
    ],
) -> FunctionCall:
    return _JSONB_EXTRACT(*args)


def JsonInsert(
    *args: *tuple[
        ExpressionOrLiteral,
        ExpressionOrLiteral,
        ExpressionOrLiteral,
        *tuple[ExpressionOrLiteral, ...],
    ],
) -> FunctionCall:
    return _JSON_INSERT(*args)


def JsonbInsert(
    *args: *tuple[
        ExpressionOrLiteral,
        ExpressionOrLiteral,
        ExpressionOrLiteral,
        *tuple[ExpressionOrLiteral, ...],
    ],
) -> FunctionCall:
    return _JSONB_INSERT(*args)


def JsonObject(*args: ExpressionOrLiteral) -> FunctionCall:
    return _JSON_OBJECT(*args)


def JsonbObject(*args: ExpressionOrLiteral) -> FunctionCall:
    return _JSONB_OBJECT(*args)


def JsonPatch(t: ExpressionOrLiteral, p: ExpressionOrLiteral, /) -> FunctionCall:
    return _JSON_PATCH(t, p)


def JsonbPatch(t: ExpressionOrLiteral, p: ExpressionOrLiteral, /) -> FunctionCall:
    return _JSONB_PATCH(t, p)


@overload
def JsonPretty(x: ExpressionOrLiteral, /) -> FunctionCall: ...
@overload
def JsonPretty(
    x: ExpressionOrLiteral, indent: ExpressionOrLiteral, /
) -> FunctionCall: ...
def JsonPretty(*args: ExpressionOrLiteral) -> FunctionCall:
    return _JSON_PRETTY(*args)


def JsonQuote(x: ExpressionOrLiteral, /) -> FunctionCall:
    return _JSON_QUOTE(x)


def JsonRemove(
    *args: *tuple[
        ExpressionOrLiteral, ExpressionOrLiteral, *tuple[ExpressionOrLiteral, ...]
    ],
) -> FunctionCall:
    return _JSON_REMOVE(*args)


def JsonbRemove(
    *args: *tuple[
        ExpressionOrLiteral, ExpressionOrLiteral, *tuple[ExpressionOrLiteral, ...]
    ],
) -> FunctionCall:
    return _JSONB_REMOVE(*args)


def JsonReplace(
    *args: *tuple[
        ExpressionOrLiteral,
        ExpressionOrLiteral,
        ExpressionOrLiteral,
        *tuple[ExpressionOrLiteral, ...],
    ],
) -> FunctionCall:
    return _JSON_REPLACE(*args)


def JsonbReplace(
    *args: *tuple[
        ExpressionOrLiteral,
        ExpressionOrLiteral,
        ExpressionOrLiteral,
        *tuple[ExpressionOrLiteral, ...],
    ],
) -> FunctionCall:
    return _JSONB_REPLACE(*args)


def JsonSet(
    *args: *tuple[
        ExpressionOrLiteral,
        ExpressionOrLiteral,
        ExpressionOrLiteral,
        *tuple[ExpressionOrLiteral, ...],
    ],
) -> FunctionCall:
    return _JSON_SET(*args)


def JsonbSet(
    *args: *tuple[
        ExpressionOrLiteral,
        ExpressionOrLiteral,
        ExpressionOrLiteral,
        *tuple[ExpressionOrLiteral, ...],
    ],
) -> FunctionCall:
    return _JSONB_SET(*args)


@overload
def JsonType(x: ExpressionOrLiteral, /) -> FunctionCall: ...
@overload
def JsonType(x: ExpressionOrLiteral, path: ExpressionOrLiteral, /) -> FunctionCall: ...
def JsonType(*args: ExpressionOrLiteral) -> FunctionCall:
    return _JSON_TYPE(*args)


@overload
def JsonValid(x: ExpressionOrLiteral, /) -> FunctionCall: ...
@overload
def JsonValid(
    x: ExpressionOrLiteral, flags: ExpressionOrLiteral, /
) -> FunctionCall: ...
def JsonValid(*args: ExpressionOrLiteral) -> FunctionCall:
    return _JSON_VALID(*args)


# ---------------------------------------------------------------------------
# JSON1 aggregate
# ---------------------------------------------------------------------------


def JsonGroupArray(
    x: ExpressionOrLiteral,
    /,
    *,
    distinct: bool = False,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall:
    return _JSON_GROUP_ARRAY(x, distinct=distinct, order_by=order_by)


def JsonbGroupArray(
    x: ExpressionOrLiteral,
    /,
    *,
    distinct: bool = False,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall:
    return _JSONB_GROUP_ARRAY(x, distinct=distinct, order_by=order_by)


def JsonGroupObject(
    label: ExpressionOrLiteral,
    value: ExpressionOrLiteral,
    /,
    *,
    distinct: bool = False,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall:
    return _JSON_GROUP_OBJECT(label, value, distinct=distinct, order_by=order_by)


def JsonbGroupObject(
    label: ExpressionOrLiteral,
    value: ExpressionOrLiteral,
    /,
    *,
    distinct: bool = False,
    order_by: tuple[OrderingTerm, ...] | None = None,
) -> FunctionCall:
    return _JSONB_GROUP_OBJECT(label, value, distinct=distinct, order_by=order_by)
