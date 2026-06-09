import pytest

from sqlinpython import Name, Rollback, Select, TableRef, TypeName
from sqlinpython import expression as expr

true = expr.literal(True)
false = expr.literal(False)
one = expr.literal(1)
two = expr.literal(2)
a = expr.literal("a")
b = expr.literal("b")


def to_str(element: expr.Expression) -> str:
    buffer: list[str] = []
    element._create_query(buffer)
    return "".join(buffer)


# ---------------------------------------------------------------------------
# Literals
# ---------------------------------------------------------------------------


def test_literal_float() -> None:
    assert to_str(expr.literal(1.0)) == "1.0"


def test_literal_float_inf_raises() -> None:
    with pytest.raises(ValueError, match="FloatLiteral"):
        _ = expr.literal(float("inf"))


def test_literal_float_negative_inf_raises() -> None:
    with pytest.raises(ValueError, match="FloatLiteral"):
        _ = expr.literal(float("-inf"))


def test_literal_float_nan_raises() -> None:
    with pytest.raises(ValueError, match="FloatLiteral"):
        _ = expr.literal(float("nan"))


def test_literal_int() -> None:
    assert to_str(expr.literal(1)) == "1"


def test_literal_string() -> None:
    assert to_str(expr.literal("hello")) == "'hello'"


def test_literal_string_empty() -> None:
    assert to_str(expr.literal("")) == "''"


def test_literal_string_with_single_quote() -> None:
    assert to_str(expr.literal("O'Reilly")) == "'O''Reilly'"


def test_literal_string_with_multiple_single_quotes() -> None:
    assert to_str(expr.literal("it's 'that'")) == "'it''s ''that'''"


def test_literal_string_with_double_quote() -> None:
    assert to_str(expr.literal('say "hi"')) == "'say \"hi\"'"


def test_literal_string_in_comparison() -> None:
    assert to_str(expr.literal("a").eq(expr.literal("b"))) == "'a' = 'b'"


def test_literal_bytes() -> None:
    assert to_str(expr.literal(b"\xff")) == "X'FF'"


def test_literal_none() -> None:
    assert to_str(expr.literal(None)) == "NULL"


def test_literal_true() -> None:
    assert to_str(expr.literal(True)) == "TRUE"


def test_literal_false() -> None:
    assert to_str(expr.literal(False)) == "FALSE"


def test_literal_current_date() -> None:
    assert to_str(expr.CurrentDate) == "CURRENT_DATE"


def test_literal_current_time() -> None:
    assert to_str(expr.CurrentTime) == "CURRENT_TIME"


def test_literal_current_timestamp() -> None:
    assert to_str(expr.CurrentTimestamp) == "CURRENT_TIMESTAMP"


# ---------------------------------------------------------------------------
# NumericLiteral
# ---------------------------------------------------------------------------


def test_numeric_literal_zero() -> None:
    assert to_str(expr.NumericLiteral("0")) == "0"


def test_numeric_literal_int() -> None:
    assert to_str(expr.NumericLiteral("123")) == "123"


def test_numeric_literal_leading_zero() -> None:
    assert to_str(expr.NumericLiteral("01")) == "01"


def test_numeric_literal_underscore_separator() -> None:
    assert to_str(expr.NumericLiteral("12_34")) == "12_34"


def test_numeric_literal_decimal() -> None:
    assert to_str(expr.NumericLiteral("1.5")) == "1.5"


def test_numeric_literal_zero_decimal() -> None:
    assert to_str(expr.NumericLiteral("0.5")) == "0.5"


def test_numeric_literal_trailing_dot() -> None:
    assert to_str(expr.NumericLiteral("1.")) == "1."


def test_numeric_literal_leading_dot() -> None:
    assert to_str(expr.NumericLiteral(".5")) == ".5"


def test_numeric_literal_decimal_with_underscore() -> None:
    assert to_str(expr.NumericLiteral("1.2_3")) == "1.2_3"


def test_numeric_literal_exponent() -> None:
    assert to_str(expr.NumericLiteral("1e10")) == "1e10"


def test_numeric_literal_exponent_uppercase() -> None:
    assert to_str(expr.NumericLiteral("1E10")) == "1E10"


def test_numeric_literal_exponent_positive_sign() -> None:
    assert to_str(expr.NumericLiteral("1e+10")) == "1e+10"


def test_numeric_literal_exponent_negative_sign() -> None:
    assert to_str(expr.NumericLiteral("1e-10")) == "1e-10"


def test_numeric_literal_exponent_underscore() -> None:
    assert to_str(expr.NumericLiteral("1e1_0")) == "1e1_0"


def test_numeric_literal_float_with_exponent() -> None:
    assert to_str(expr.NumericLiteral("1.5e10")) == "1.5e10"


def test_numeric_literal_leading_dot_with_exponent() -> None:
    assert to_str(expr.NumericLiteral(".5e10")) == ".5e10"


def test_numeric_literal_hex() -> None:
    assert to_str(expr.NumericLiteral("0xFF")) == "0xFF"


def test_numeric_literal_hex_uppercase_prefix() -> None:
    assert to_str(expr.NumericLiteral("0X1A")) == "0X1A"


def test_numeric_literal_hex_with_underscore() -> None:
    assert to_str(expr.NumericLiteral("0xFF_FF")) == "0xFF_FF"


def test_numeric_literal_in_comparison() -> None:
    assert (
        to_str(expr.NumericLiteral("0xFF").eq(expr.NumericLiteral("255")))
        == "0xFF = 255"
    )


def test_numeric_literal_empty_raises() -> None:
    with pytest.raises(ValueError, match="Numeric literal"):
        _ = expr.NumericLiteral("")


def test_numeric_literal_only_dot_raises() -> None:
    with pytest.raises(ValueError, match="Numeric literal"):
        _ = expr.NumericLiteral(".")


def test_numeric_literal_trailing_underscore_raises() -> None:
    with pytest.raises(ValueError, match="Numeric literal"):
        _ = expr.NumericLiteral("1_")


def test_numeric_literal_incomplete_exponent_raises() -> None:
    with pytest.raises(ValueError, match="Numeric literal"):
        _ = expr.NumericLiteral("1e")


def test_numeric_literal_incomplete_exponent_sign_raises() -> None:
    with pytest.raises(ValueError, match="Numeric literal"):
        _ = expr.NumericLiteral("1e+")


def test_numeric_literal_incomplete_hex_raises() -> None:
    with pytest.raises(ValueError, match="Numeric literal"):
        _ = expr.NumericLiteral("0x")


def test_numeric_literal_hex_trailing_underscore_raises() -> None:
    with pytest.raises(ValueError, match="Numeric literal"):
        _ = expr.NumericLiteral("0xFF_")


def test_numeric_literal_double_dot_raises() -> None:
    with pytest.raises(ValueError, match="Numeric literal"):
        _ = expr.NumericLiteral("1.2_3.4")


def test_numeric_literal_double_underscore_raises() -> None:
    with pytest.raises(ValueError, match="Numeric literal"):
        _ = expr.NumericLiteral("1.2__3")


def test_numeric_literal_invalid_char_raises() -> None:
    with pytest.raises(ValueError, match="Numeric literal"):
        _ = expr.NumericLiteral("abc")


def test_numeric_literal_non_ascii_digit_raises() -> None:
    with pytest.raises(ValueError, match="Numeric literal"):
        _ = expr.NumericLiteral("١")


# ---------------------------------------------------------------------------
# HexLiteral
# ---------------------------------------------------------------------------


def test_hex_literal_basic() -> None:
    assert to_str(expr.HexLiteral(0xFF)) == "0xFF"


def test_hex_literal_zero() -> None:
    assert to_str(expr.HexLiteral(0)) == "0x0"


def test_hex_literal_decimal_input() -> None:
    assert to_str(expr.HexLiteral(255)) == "0xFF"


def test_hex_literal_uppercase_output() -> None:
    assert to_str(expr.HexLiteral(0xDEADBEEF)) == "0xDEADBEEF"


def test_hex_literal_large() -> None:
    assert to_str(expr.HexLiteral(0xFFFFFFFFFFFFFFFF)) == "0xFFFFFFFFFFFFFFFF"


def test_hex_literal_in_comparison() -> None:
    assert to_str(expr.HexLiteral(0xFF).eq(expr.HexLiteral(0xFF))) == "0xFF = 0xFF"


def test_hex_literal_negative_raises() -> None:
    with pytest.raises(ValueError, match="negative"):
        _ = expr.HexLiteral(-1)


# ---------------------------------------------------------------------------
# BlobLiteral
# ---------------------------------------------------------------------------


def test_blob_literal_basic() -> None:
    assert to_str(expr.BlobLiteral(b"\xff")) == "X'FF'"


def test_blob_literal_multiple_bytes() -> None:
    assert to_str(expr.BlobLiteral(b"SQLite")) == "X'53514C697465'"


def test_blob_literal_empty() -> None:
    assert to_str(expr.BlobLiteral(b"")) == "X''"


def test_blob_literal_zero_byte() -> None:
    assert to_str(expr.BlobLiteral(b"\x00")) == "X'00'"


def test_blob_literal_uppercase_output() -> None:
    assert to_str(expr.BlobLiteral(b"\xab\xcd")) == "X'ABCD'"


def test_blob_literal_in_comparison() -> None:
    assert (
        to_str(expr.BlobLiteral(b"\xff").eq(expr.BlobLiteral(b"\xff")))
        == "X'FF' = X'FF'"
    )


# ---------------------------------------------------------------------------
# OR / AND operators
# ---------------------------------------------------------------------------


def test_or_basic() -> None:
    assert to_str(true.Or(false)) == "TRUE OR FALSE"


def test_or_chained() -> None:
    assert to_str(true.Or(false).Or(true)) == "TRUE OR FALSE OR TRUE"


def test_or_and_parentheses() -> None:
    assert to_str(true.Or(false).And(true)) == "(TRUE OR FALSE) AND TRUE"


def test_and_basic() -> None:
    assert to_str(true.And(false)) == "TRUE AND FALSE"


def test_and_chained() -> None:
    assert to_str(true.And(false).And(true)) == "TRUE AND FALSE AND TRUE"


def test_and_or_no_parentheses() -> None:
    assert to_str(true.And(false).Or(true)) == "TRUE AND FALSE OR TRUE"


# ---------------------------------------------------------------------------
# NOT operator
# ---------------------------------------------------------------------------


def test_not_basic() -> None:
    assert to_str(expr.Not(false)) == "NOT FALSE"


def test_not_parenthesized_in_is() -> None:
    assert to_str(true.Is(expr.Not(false))) == "TRUE IS (NOT FALSE)"


# ---------------------------------------------------------------------------
# IS operator
# ---------------------------------------------------------------------------


def test_is_basic() -> None:
    assert to_str(true.Is(false)) == "TRUE IS FALSE"


def test_is_null() -> None:
    n = expr.literal(None)
    assert to_str(n.Is(n)) == "NULL IS NULL"


def test_is_not() -> None:
    assert to_str(true.Is.Not(false)) == "TRUE IS NOT FALSE"


def test_is_distinct_from() -> None:
    assert to_str(true.Is.DistinctFrom(false)) == "TRUE IS DISTINCT FROM FALSE"


def test_is_not_distinct_from() -> None:
    assert to_str(true.Is.Not.DistinctFrom(false)) == "TRUE IS NOT DISTINCT FROM FALSE"


# ---------------------------------------------------------------------------
# Equality operators
# ---------------------------------------------------------------------------


def test_eq_single() -> None:
    assert to_str(true.eq(false, double_eq=False)) == "TRUE = FALSE"


def test_eq_double() -> None:
    assert to_str(true.eq(false, double_eq=True)) == "TRUE == FALSE"


def test_ne_arrows() -> None:
    assert to_str(true.ne(false, arrows=True)) == "TRUE <> FALSE"


def test_ne_bang() -> None:
    assert to_str(true.ne(false, arrows=False)) == "TRUE != FALSE"


# ---------------------------------------------------------------------------
# Auto-parentheses
# ---------------------------------------------------------------------------


def test_auto_parentheses_not_of_and() -> None:
    assert (
        to_str(expr.Not(true.Or(false).And(true))) == "NOT ((TRUE OR FALSE) AND TRUE)"
    )


def test_auto_parentheses_not_and_or() -> None:
    assert to_str(expr.Not(true).And(false).Or(true)) == "NOT TRUE AND FALSE OR TRUE"


# ---------------------------------------------------------------------------
# IN operator
# ---------------------------------------------------------------------------


def test_in_empty() -> None:
    assert to_str(true.In()) == "TRUE IN ()"


def test_in_values() -> None:
    assert to_str(true.In(true, false)) == "TRUE IN (TRUE, FALSE)"


def test_in_table_name() -> None:
    assert to_str(true.In(Name("a"))) == "TRUE IN a"


def test_in_table_name_quoted() -> None:
    assert to_str(true.In(Name('a"'))) == 'TRUE IN "a"""'


def test_in_schema_table() -> None:
    assert to_str(true.In(Name("a"), Name("b"))) == "TRUE IN a.b"


def test_in_schema_table_quoted() -> None:
    assert to_str(true.In(Name('a"'), Name('b"'))) == 'TRUE IN "a"""."b"""'


def test_not_in_empty() -> None:
    assert to_str(true.Not.In()) == "TRUE NOT IN ()"


def test_not_in_values() -> None:
    assert to_str(true.Not.In(true, false)) == "TRUE NOT IN (TRUE, FALSE)"


def test_not_in_table_name() -> None:
    assert to_str(true.Not.In(Name("a"))) == "TRUE NOT IN a"


def test_not_in_table_name_quoted() -> None:
    assert to_str(true.Not.In(Name('a"'))) == 'TRUE NOT IN "a"""'


def test_not_in_schema_table() -> None:
    assert to_str(true.Not.In(Name("a"), Name("b"))) == "TRUE NOT IN a.b"


def test_not_in_schema_table_quoted() -> None:
    assert to_str(true.Not.In(Name('a"'), Name('b"'))) == 'TRUE NOT IN "a"""."b"""'


def test_in_not_expression_parenthesized() -> None:
    assert to_str(expr.Not(true).In()) == "(NOT TRUE) IN ()"


# ---------------------------------------------------------------------------
# LIKE / GLOB / REGEXP / MATCH
# ---------------------------------------------------------------------------


def test_like_basic() -> None:
    assert to_str(true.Like(false)) == "TRUE LIKE FALSE"


def test_not_like() -> None:
    assert to_str(true.Not.Like(false)) == "TRUE NOT LIKE FALSE"


def test_like_not_expr_parenthesized() -> None:
    assert to_str(true.Like(expr.Not(false))) == "TRUE LIKE (NOT FALSE)"


def test_like_escape() -> None:
    assert to_str(true.Like(false).Escape(true)) == "TRUE LIKE FALSE ESCAPE TRUE"


def test_like_not_expr_escape() -> None:
    assert (
        to_str(true.Like(expr.Not(false)).Escape(true))
        == "TRUE LIKE (NOT FALSE) ESCAPE TRUE"
    )


def test_like_escape_with_not() -> None:
    assert (
        to_str(true.Like(false).Escape(expr.Not(true)))
        == "TRUE LIKE FALSE ESCAPE (NOT TRUE)"
    )


def test_like_escape_with_or() -> None:
    assert (
        to_str(true.Like(false).Escape(true.Or(false)))
        == "TRUE LIKE FALSE ESCAPE (TRUE OR FALSE)"
    )


def test_like_escape_with_like() -> None:
    assert (
        to_str(true.Like(false).Escape(true.Like(false)))
        == "TRUE LIKE FALSE ESCAPE (TRUE LIKE FALSE)"
    )


def test_glob_basic() -> None:
    assert to_str(true.Glob(false)) == "TRUE GLOB FALSE"


def test_not_glob() -> None:
    assert to_str(true.Not.Glob(false)) == "TRUE NOT GLOB FALSE"


def test_glob_not_expr_parenthesized() -> None:
    assert to_str(true.Glob(expr.Not(false))) == "TRUE GLOB (NOT FALSE)"


def test_regexp_basic() -> None:
    assert to_str(true.Regexp(false)) == "TRUE REGEXP FALSE"


def test_not_regexp() -> None:
    assert to_str(true.Not.Regexp(false)) == "TRUE NOT REGEXP FALSE"


def test_regexp_not_expr_parenthesized() -> None:
    assert to_str(true.Regexp(expr.Not(false))) == "TRUE REGEXP (NOT FALSE)"


def test_match_basic() -> None:
    assert to_str(true.Match(false)) == "TRUE MATCH FALSE"


def test_not_match() -> None:
    assert to_str(true.Not.Match(false)) == "TRUE NOT MATCH FALSE"


def test_match_not_expr_parenthesized() -> None:
    assert to_str(true.Match(expr.Not(false))) == "TRUE MATCH (NOT FALSE)"


# ---------------------------------------------------------------------------
# NULL comparisons
# ---------------------------------------------------------------------------


def test_isnull() -> None:
    assert to_str(true.IsNull) == "TRUE ISNULL"


def test_notnull() -> None:
    assert to_str(true.Notnull) == "TRUE NOTNULL"


def test_not_null() -> None:
    assert to_str(true.Not.Null) == "TRUE NOT NULL"


# ---------------------------------------------------------------------------
# Comparison operators
# ---------------------------------------------------------------------------


def test_lt_basic() -> None:
    assert to_str(one < two) == "1 < 2"


def test_lt_rhs_addition() -> None:
    assert to_str(one < two + one) == "1 < 2 + 1"


def test_lt_result_addition() -> None:
    assert to_str((one < two) + one) == "(1 < 2) + 1"


def test_le_basic() -> None:
    assert to_str(one <= two) == "1 <= 2"


def test_le_lhs_subtraction() -> None:
    assert to_str(one - two <= one) == "1 - 2 <= 1"


def test_le_rhs_parenthesized() -> None:
    assert to_str(one - (two <= one)) == "1 - (2 <= 1)"


def test_gt_basic() -> None:
    assert to_str(one > two) == "1 > 2"


def test_gt_rhs_subtraction() -> None:
    assert to_str(one > two - one) == "1 > 2 - 1"


def test_gt_result_subtraction() -> None:
    assert to_str((one > two) - one) == "(1 > 2) - 1"


def test_ge_basic() -> None:
    assert to_str(one >= two) == "1 >= 2"


def test_ge_lhs_addition() -> None:
    assert to_str(one + two >= one) == "1 + 2 >= 1"


def test_ge_rhs_parenthesized() -> None:
    assert to_str(one + (two >= one)) == "1 + (2 >= 1)"


# ---------------------------------------------------------------------------
# Arithmetic operators
# ---------------------------------------------------------------------------


def test_add_basic() -> None:
    assert to_str(one + two) == "1 + 2"


def test_add_chained() -> None:
    assert to_str(one + two + one) == "1 + 2 + 1"


def test_add_rhs_parenthesized() -> None:
    assert to_str(one + (two + one)) == "1 + (2 + 1)"


def test_sub_basic() -> None:
    assert to_str(one - two) == "1 - 2"


def test_sub_chained() -> None:
    assert to_str(one - two - one) == "1 - 2 - 1"


def test_sub_rhs_parenthesized() -> None:
    assert to_str(one - (two - one)) == "1 - (2 - 1)"


def test_mul_basic() -> None:
    assert to_str(one * two) == "1 * 2"


def test_mul_chained() -> None:
    assert to_str(one * two * one) == "1 * 2 * 1"


def test_mul_rhs_parenthesized() -> None:
    assert to_str(one * (two * one)) == "1 * (2 * 1)"


def test_div_basic() -> None:
    assert to_str(one / two) == "1 / 2"


def test_div_chained() -> None:
    assert to_str(one / two / one) == "1 / 2 / 1"


def test_div_rhs_parenthesized() -> None:
    assert to_str(one / (two / one)) == "1 / (2 / 1)"


def test_mod_basic() -> None:
    assert to_str(one % two) == "1 % 2"


def test_mod_chained() -> None:
    assert to_str(one % two % one) == "1 % 2 % 1"


def test_mod_rhs_parenthesized() -> None:
    assert to_str(one % (two % one)) == "1 % (2 % 1)"


def test_add_mul_precedence() -> None:
    assert to_str(one + two * one) == "1 + 2 * 1"


def test_add_mul_lhs_parenthesized() -> None:
    assert to_str((one + two) * one) == "(1 + 2) * 1"


def test_add_div_add() -> None:
    assert to_str(one + two / one + two) == "1 + 2 / 1 + 2"


def test_mixed_add_mul_sub() -> None:
    assert to_str((one + two) * (one - two)) == "(1 + 2) * (1 - 2)"


# ---------------------------------------------------------------------------
# Concatenation / extraction operators
# ---------------------------------------------------------------------------


def test_concat_basic() -> None:
    assert to_str(a.Concat(b)) == "'a' || 'b'"


def test_concat_chained() -> None:
    assert to_str(a.Concat(b).Concat(a)) == "'a' || 'b' || 'a'"


def test_concat_rhs_parenthesized() -> None:
    assert to_str(a.Concat(b.Concat(a))) == "'a' || ('b' || 'a')"


def test_extract_basic() -> None:
    assert to_str(a.Extract(b)) == "'a' -> 'b'"


def test_extract_chained() -> None:
    assert to_str(a.Extract(b).Extract(a)) == "'a' -> 'b' -> 'a'"


def test_extract_rhs_parenthesized() -> None:
    assert to_str(a.Extract(b.Extract(a))) == "'a' -> ('b' -> 'a')"


def test_extract2_basic() -> None:
    assert to_str(a.Extract2(b)) == "'a' ->> 'b'"


def test_extract2_chained_extract() -> None:
    assert to_str(a.Extract2(b).Extract(a)) == "'a' ->> 'b' -> 'a'"


def test_extract_chained_extract2() -> None:
    assert to_str(a.Extract(b.Extract2(a))) == "'a' -> ('b' ->> 'a')"


# ---------------------------------------------------------------------------
# Unary operators
# ---------------------------------------------------------------------------


def test_unary_neg() -> None:
    assert to_str(-one) == "-1"


def test_unary_pos() -> None:
    assert to_str(+one) == "+1"


def test_unary_invert() -> None:
    assert to_str(~one) == "~1"


def test_unary_neg_add() -> None:
    assert to_str(-two + one) == "-2 + 1"


def test_unary_pos_rhs() -> None:
    assert to_str(one + (+two)) == "1 + +2"


def test_unary_invert_add() -> None:
    assert to_str(~two + one) == "~2 + 1"


# ---------------------------------------------------------------------------
# Bind parameters
# ---------------------------------------------------------------------------


def test_bind_parameter_positional() -> None:
    assert to_str(expr.BindParameter()) == "?"


def test_bind_parameter_numbered() -> None:
    assert to_str(expr.BindParameter(2)) == "?2"


def test_bind_parameter_named_colon_default() -> None:
    assert to_str(expr.BindParameter("id")) == ":id"


def test_bind_parameter_named_colon_explicit() -> None:
    assert to_str(expr.BindParameter("id", ":")) == ":id"


def test_bind_parameter_named_at() -> None:
    assert to_str(expr.BindParameter("id", "@")) == "@id"


def test_bind_parameter_named_dollar() -> None:
    assert to_str(expr.BindParameter("id", "$")) == "$id"


# ---------------------------------------------------------------------------
# CASE expression
# ---------------------------------------------------------------------------


def test_case_when_then_end() -> None:
    assert (
        to_str(expr.Case.When(expr.literal(1)).Then(expr.literal(2)).End)
        == "CASE WHEN 1 THEN 2 END"
    )


def test_case_when_then_else_end() -> None:
    assert (
        to_str(
            expr.Case.When(expr.literal(1))
            .Then(expr.literal(2))
            .Else(expr.literal(3))
            .End
        )
        == "CASE WHEN 1 THEN 2 ELSE 3 END"
    )


def test_case_operand_when_then_end() -> None:
    assert (
        to_str(
            expr.Case(expr.literal("a")).When(expr.literal(1)).Then(expr.literal(2)).End
        )
        == "CASE 'a' WHEN 1 THEN 2 END"
    )


def test_case_operand_when_then_else_end() -> None:
    assert (
        to_str(
            expr.Case(expr.literal("a"))
            .When(expr.literal(1))
            .Then(expr.literal(2))
            .Else(expr.literal(3))
            .End
        )
        == "CASE 'a' WHEN 1 THEN 2 ELSE 3 END"
    )


def test_case_multiple_when_then() -> None:
    assert (
        to_str(
            expr.Case.When(expr.literal(1))
            .Then(expr.literal(2))
            .When(expr.literal(3))
            .Then(expr.literal(4))
            .End
        )
        == "CASE WHEN 1 THEN 2 WHEN 3 THEN 4 END"
    )


def test_case_multiple_when_then_else() -> None:
    assert (
        to_str(
            expr.Case.When(expr.literal(1))
            .Then(expr.literal(2))
            .When(expr.literal(3))
            .Then(expr.literal(4))
            .Else(expr.literal(5))
            .End
        )
        == "CASE WHEN 1 THEN 2 WHEN 3 THEN 4 ELSE 5 END"
    )


# ---------------------------------------------------------------------------
# Row value (parenthesized expression list / tuple)
# ---------------------------------------------------------------------------


def test_row_two_elements() -> None:
    assert to_str(expr.Row(one, two)) == "(1, 2)"


def test_row_three_elements() -> None:
    assert to_str(expr.Row(one, two, a)) == "(1, 2, 'a')"


def test_row_mixed_operators_not_wrapped() -> None:
    # Inside parens, low-precedence sub-expressions need no extra wrapping.
    assert to_str(expr.Row(true.Or(false), one + two)) == "(TRUE OR FALSE, 1 + 2)"


def test_row_nested() -> None:
    assert to_str(expr.Row(expr.Row(one, two), a)) == "((1, 2), 'a')"


def test_row_in_values() -> None:
    assert (
        to_str(expr.Row(one, two).In(expr.Row(one, two), expr.Row(a, b)))
        == "(1, 2) IN ((1, 2), ('a', 'b'))"
    )


def test_row_eq_row() -> None:
    assert to_str(expr.Row(one, two).eq(expr.Row(a, b))) == "(1, 2) = ('a', 'b')"


def test_row_too_few_elements_fails_type_check() -> None:
    _ = expr.Row(one)  # type: ignore[call-arg] # pyright: ignore[reportCallIssue]
    # ty doesn't currently identify this error -ty: ignore[missing-argument]
    _ = expr.Row()  # type: ignore[call-arg] # pyright: ignore[reportCallIssue]
    # ty doesn't currently identify this error -ty: ignore[missing-argument]


def test_row_accepts_python_literals() -> None:
    assert to_str(expr.Row(1, 2)) == "(1, 2)"
    assert to_str(expr.Row(1, "a", 2)) == "(1, 'a', 2)"


# ---------------------------------------------------------------------------
# CAST(expr AS type-name)
# ---------------------------------------------------------------------------


def test_cast_basic() -> None:
    assert to_str(expr.Cast(one, TypeName("INTEGER"))) == "CAST(1 AS INTEGER)"


def test_cast_inner_expression_not_wrapped() -> None:
    assert to_str(expr.Cast(one + two, TypeName("INTEGER"))) == "CAST(1 + 2 AS INTEGER)"


def test_cast_type_with_one_arg() -> None:
    assert to_str(expr.Cast(a, TypeName("VARCHAR")(10))) == "CAST('a' AS VARCHAR(10))"


def test_cast_type_with_two_args() -> None:
    assert (
        to_str(expr.Cast(a, TypeName("DECIMAL")(10, 2)))
        == "CAST('a' AS DECIMAL(10, 2))"
    )


def test_cast_nested() -> None:
    assert (
        to_str(expr.Cast(expr.Cast(one, TypeName("FLOAT")), TypeName("INTEGER")))
        == "CAST(CAST(1 AS FLOAT) AS INTEGER)"
    )


def test_cast_inside_comparison_not_parenthesized() -> None:
    assert (
        to_str(expr.Cast(one, TypeName("INTEGER")).eq(two)) == "CAST(1 AS INTEGER) = 2"
    )


def test_cast_inside_in() -> None:
    assert (
        to_str(one.In(expr.Cast(a, TypeName("INTEGER"))))
        == "1 IN (CAST('a' AS INTEGER))"
    )


# ---------------------------------------------------------------------------
# EXISTS / NOT EXISTS / bare subquery
# ---------------------------------------------------------------------------

_subselect = Select("*").From(TableRef("t"))
_subselect_sql = "SELECT * FROM t"


def test_exists_basic() -> None:
    assert to_str(expr.Exists(_subselect)) == f"EXISTS ({_subselect_sql})"


def test_not_exists() -> None:
    assert to_str(expr.Not(expr.Exists(_subselect))) == f"NOT EXISTS ({_subselect_sql})"


def test_not_exists_via_method() -> None:
    assert to_str(expr.Not.Exists(_subselect)) == f"NOT EXISTS ({_subselect_sql})"


def test_exists_in_and() -> None:
    assert (
        to_str(expr.Exists(_subselect).And(true))
        == f"EXISTS ({_subselect_sql}) AND TRUE"
    )


def test_subquery_basic() -> None:
    assert to_str(expr.Subquery(_subselect)) == f"({_subselect_sql})"


def test_subquery_in_comparison() -> None:
    assert to_str(expr.Subquery(_subselect).eq(one)) == f"({_subselect_sql}) = 1"


def test_subquery_in_arithmetic() -> None:
    assert to_str(expr.Subquery(_subselect) + one) == f"({_subselect_sql}) + 1"


# ---------------------------------------------------------------------------
# RAISE(...) function
# ---------------------------------------------------------------------------


def test_raise_ignore() -> None:
    expected = "RAISE(IGNORE)"
    assert to_str(expr.Raise.Ignore) == expected
    assert to_str(expr.Raise("IGNORE")) == expected
    assert to_str(expr.Raise(expr.Ignore)) == expected


def test_raise_rollback() -> None:
    expected = "RAISE(ROLLBACK, 'oops')"
    assert to_str(expr.Raise.Rollback("oops")) == expected
    assert to_str(expr.Raise("ROLLBACK", "oops")) == expected
    assert to_str(expr.Raise(Rollback, "oops")) == expected


def test_raise_abort() -> None:
    expected = "RAISE(ABORT, 'constraint failed')"
    assert to_str(expr.Raise.Abort("constraint failed")) == expected
    assert to_str(expr.Raise("ABORT", "constraint failed")) == expected
    assert to_str(expr.Raise(expr.Abort, "constraint failed")) == expected


def test_raise_fail() -> None:
    expected = "RAISE(FAIL, 'nope')"
    assert to_str(expr.Raise.Fail("nope")) == expected
    assert to_str(expr.Raise("FAIL", "nope")) == expected
    assert to_str(expr.Raise(expr.Fail, "nope")) == expected


def test_raise_message_is_expression() -> None:
    assert to_str(expr.Raise.Fail(a.Concat(b))) == "RAISE(FAIL, 'a' || 'b')"


def test_raise_inside_case() -> None:
    assert (
        to_str(expr.Case.When(one.eq(two)).Then(expr.Raise.Ignore).End)
        == "CASE WHEN 1 = 2 THEN RAISE(IGNORE) END"
    )


def test_raise_inside_or() -> None:
    assert (
        to_str(expr.Raise.Ignore.Or(expr.Raise.Fail("x")))
        == "RAISE(IGNORE) OR RAISE(FAIL, 'x')"
    )


# ---------------------------------------------------------------------------
# SqlLiteral coercion on Expression operators/comparisons/builders
# ---------------------------------------------------------------------------


def test_expression_eq_accepts_python_literal() -> None:
    assert to_str(a.eq(1)) == "'a' = 1"


def test_expression_ne_accepts_python_literal() -> None:
    assert to_str(a.ne("b")) == "'a' != 'b'"


def test_expression_lt_accepts_python_literal() -> None:
    assert to_str(one < 2) == "1 < 2"


def test_expression_add_accepts_python_literal() -> None:
    assert to_str(one + 2) == "1 + 2"


def test_expression_sub_accepts_python_literal() -> None:
    assert to_str(one - 2) == "1 - 2"


def test_expression_mul_accepts_python_literal() -> None:
    assert to_str(one * 2) == "1 * 2"


def test_expression_concat_accepts_python_literal() -> None:
    assert to_str(a.Concat("z")) == "'a' || 'z'"


def test_expression_and_or_accept_python_literals() -> None:
    assert to_str(one.And(2).Or(3)) == "1 AND 2 OR 3"


def test_expression_between_accepts_python_literals() -> None:
    assert to_str(one.Between(0, 10)) == "1 BETWEEN 0 AND 10"


def test_expression_in_accepts_python_literals() -> None:
    assert to_str(one.In(1, 2, 3)) == "1 IN (1, 2, 3)"


def test_expression_like_accepts_python_literal() -> None:
    assert to_str(a.Like("%x%")) == "'a' LIKE '%x%'"


def test_expression_like_escape_accepts_python_literal() -> None:
    assert to_str(a.Like("%x%").Escape("\\")) == "'a' LIKE '%x%' ESCAPE '\\'"


def test_expression_glob_accepts_python_literal() -> None:
    assert to_str(a.Glob("*.txt")) == "'a' GLOB '*.txt'"


def test_not_accepts_python_literal() -> None:
    assert to_str(expr.Not(1)) == "NOT 1"


def test_is_accepts_python_literal() -> None:
    assert to_str(one.Is(2)) == "1 IS 2"


def test_raise_message_none_is_sql_null() -> None:
    assert to_str(expr.Raise("FAIL", None)) == "RAISE(FAIL, NULL)"


# ---------------------------------------------------------------------------
# Reflected operators (literal on the left side)
# ---------------------------------------------------------------------------


def test_reflected_add() -> None:
    assert to_str(5 + one) == "5 + 1"


def test_reflected_sub_preserves_order() -> None:
    # Non-commutative: 5 - col must NOT equal col - 5
    assert to_str(5 - one) == "5 - 1"
    assert to_str(one - 5) == "1 - 5"


def test_reflected_mul() -> None:
    assert to_str(5 * one) == "5 * 1"


def test_reflected_truediv_preserves_order() -> None:
    assert to_str(5 / one) == "5 / 1"


def test_reflected_mod_preserves_order() -> None:
    assert to_str(5 % one) == "5 % 1"


def test_reflected_and() -> None:
    assert to_str(5 & one) == "5 & 1"


def test_reflected_or() -> None:
    assert to_str(5 | one) == "5 | 1"


def test_reflected_lshift_preserves_order() -> None:
    assert to_str(5 << one) == "5 << 1"


def test_reflected_rshift_preserves_order() -> None:
    assert to_str(5 >> one) == "5 >> 1"


def test_reflected_comparison_via_python_reflection() -> None:
    # Python automatically routes `5 < col` to col.__gt__(5)
    assert to_str(5 < one) == "1 > 5"
