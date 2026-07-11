import pytest

from sqlinpython import Cast, ColumnDef, Create, Name, Select, TypeName, col, types
from sqlinpython.type_name import CompleteTypeName


def to_str(element: CompleteTypeName) -> str:
    buffer: list[str] = []
    element._create_query(buffer)
    return "".join(buffer)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_bare_constant() -> None:
    assert to_str(types.Integer) == "INTEGER"


def test_multi_word_constants() -> None:
    assert to_str(types.DoublePrecision) == "DOUBLE PRECISION"
    assert to_str(types.UnsignedBigInt) == "UNSIGNED BIG INT"


def test_constant_not_callable_fails_type_check() -> None:
    types.Integer(5)  # type: ignore[operator] # pyright: ignore[reportCallIssue] # ty: ignore[call-non-callable]


# ---------------------------------------------------------------------------
# Wrapper functions (types that require arguments)
# ---------------------------------------------------------------------------


def test_wrapper_with_length() -> None:
    assert to_str(types.Varchar(255)) == "VARCHAR(255)"
    assert to_str(types.NativeCharacter(70)) == "NATIVE CHARACTER(70)"


def test_decimal() -> None:
    assert to_str(types.Decimal(10)) == "DECIMAL(10)"
    assert to_str(types.Decimal(10, 2)) == "DECIMAL(10, 2)"


def test_wrapper_without_args_fails_type_check() -> None:
    with pytest.raises(TypeError):
        types.Varchar()  # type: ignore[call-arg] # pyright: ignore[reportCallIssue] # ty: ignore[missing-argument]


# ---------------------------------------------------------------------------
# TypeName with multiple names
# ---------------------------------------------------------------------------


def test_type_name_multiple_names() -> None:
    assert to_str(TypeName("DOUBLE", "PRECISION")) == "DOUBLE PRECISION"


def test_type_name_multiple_names_with_args() -> None:
    assert to_str(TypeName("VARYING", "CHARACTER")(255)) == "VARYING CHARACTER(255)"


def test_type_name_accepts_name_objects() -> None:
    assert to_str(TypeName(Name("DOUBLE"), "PRECISION")) == "DOUBLE PRECISION"


def test_type_name_single_name_with_space_is_quoted() -> None:
    # One argument is one name; a multi-word type is passed as several names.
    assert to_str(TypeName("DOUBLE PRECISION")) == '"DOUBLE PRECISION"'


def test_type_name_no_args_fails_type_check() -> None:
    _ = TypeName()  # type: ignore[call-arg] # pyright: ignore[reportCallIssue]
    # ty doesn't currently identify this error -ty: ignore[missing-argument]


# ---------------------------------------------------------------------------
# End-to-end
# ---------------------------------------------------------------------------


def test_column_def_with_types_module() -> None:
    q = Create.Table("users")(
        ColumnDef("id")(types.Integer),
        ColumnDef("name")(types.Varchar(255)),
    )
    assert q.get_query() == "CREATE TABLE users (id INTEGER, name VARCHAR(255))"


def test_cast_with_types_module() -> None:
    q = Select(Cast(col("a"), types.Decimal(10, 2)))
    assert q.get_query() == "SELECT CAST(a AS DECIMAL(10, 2))"
