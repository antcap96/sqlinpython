# TODO: Expression

Tracks remaining work on the `expression/` package against the
[SQLite expression grammar](https://sqlite.org/lang_expr.html).

## Missing expression forms

From the TODO at the bottom of `src/sqlinpython/expression/core.py`:

- [x] **tuple** — `(expr, expr, ...)` parenthesized expression list (row value, used in `(a, b) IN (...)`, `(a, b) = (SELECT x, y ...)`, etc.) — implemented as `expr.Row(first, second, *rest)`
- [x] **cast** — `CAST(expr AS type-name)` — implemented as `expr.Cast(expression, type_name)` where `type_name` is a `CompleteTypeName` (e.g. `TypeName("INTEGER")` or `TypeName("DECIMAL")(10, 2)`)
- [x] **Exists** — `[NOT] EXISTS (select-stmt)`, plus the related bare subquery-as-expression `(select-stmt)` — implemented as `expr.Exists(select_stmt)`, `expr.Not.Exists(select_stmt)` (or `expr.Not(expr.Exists(select_stmt))`), and `expr.Subquery(select_stmt)`. The expression-position `Subquery` is a distinct class from the FROM-clause `Subquery` (`sqlinpython.table_or_subquery.Subquery`) — same SQL output, separate types so FROM-clause subqueries don't accidentally pick up expression methods.
- [ ] **raise-function** — `RAISE(IGNORE)` and `RAISE(ROLLBACK|ABORT|FAIL, error-message)`

## Missing `literal-value` variants

Against the [`literal-value` grammar](https://sqlite.org/syntax/literal-value.html); see `# TODO: All this` at `src/sqlinpython/expression/literal.py:51`.

- [ ] **Hexadecimal integer literals** — `0xFF` form. `IntLiteral` always emits decimal; there is no way to produce hex.
- [ ] **BLOB literals** — `X'53514C697465'` / `x'...'`. No `BlobLiteral` class exists.

### Broken / limited (not strictly missing)

- [ ] `StringLiteral` uses **double quotes** (`literal.py:72`: `f'"{self._value}"'`). SQLite string literals are single-quoted; double-quoted tokens are identifiers (with a legacy fallback). It also performs no escaping — a value containing `"` produces broken SQL.
- [ ] `FloatLiteral` relies on `str(float)`, which silently turns `1.5e10` into `15000000000.0`, can emit `inf`/`nan`, and loses control over precision/notation.

## Other notes in the expression package

- `src/sqlinpython/expression/core.py:559` — refactor idea for `LikeExpressionWithEscape` so some expressions can skip parentheses (not missing functionality).
- `src/sqlinpython/expression/bind_parameter.py:22` — special case for `$`-style bind parameters (rare numbered/Tcl-style form).
