from sqlinpython import Select, TableRef, literal

# ---------------------------------------------------------------------------
# Type-level tests (verify type checkers reject invalid compound operands)
# ---------------------------------------------------------------------------


def test_union_rejects_ordered_subselect() -> None:
    _ = (
        Select("*")
        .From(TableRef("a"))
        .Union(
            Select("*").From(TableRef("b")).OrderBy(literal(1).Asc)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
            # ty doesn't currently identify this error -ty: ignore[invalid-argument-type]
        )
    )


def test_union_rejects_limited_subselect() -> None:
    _ = (
        Select("*")
        .From(TableRef("a"))
        .Union(
            Select("*").From(TableRef("b")).Limit(literal(10))  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
            # ty doesn't currently identify this error -ty: ignore[invalid-argument-type]
        )
    )
