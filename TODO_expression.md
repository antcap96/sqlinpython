# TODO: Expression

Tracks remaining work on the `expression/` package against the
[SQLite expression grammar](https://sqlite.org/lang_expr.html).

## Missing expression forms

From the TODO at the bottom of `src/sqlinpython/expression/core.py`:

- [x] **tuple** — `(expr, expr, ...)` parenthesized expression list (row value, used in `(a, b) IN (...)`, `(a, b) = (SELECT x, y ...)`, etc.) — implemented as `expr.Row(first, second, *rest)`
- [x] **cast** — `CAST(expr AS type-name)` — implemented as `expr.Cast(expression, type_name)` where `type_name` is a `CompleteTypeName` (e.g. `TypeName("INTEGER")` or `TypeName("DECIMAL")(10, 2)`)
- [x] **Exists** — `[NOT] EXISTS (select-stmt)`, plus the related bare subquery-as-expression `(select-stmt)` — implemented as `expr.Exists(select_stmt)`, `expr.Not.Exists(select_stmt)` (or `expr.Not(expr.Exists(select_stmt))`), and `expr.Subquery(select_stmt)`. The expression-position `Subquery` is a distinct class from the FROM-clause `Subquery` (`sqlinpython.table_or_subquery.Subquery`) — same SQL output, separate types so FROM-clause subqueries don't accidentally pick up expression methods.
- [x] **raise-function** — `RAISE(IGNORE)` and `RAISE(ROLLBACK|ABORT|FAIL, error-message)` — implemented as `expr.Raise.Ignore` / `expr.Raise.Rollback(msg)` / `expr.Raise.Abort(msg)` / `expr.Raise.Fail(msg)`, also callable as `expr.Raise("IGNORE")` / `expr.Raise("ROLLBACK", msg)` (string-mode), or `expr.Raise(expr.Ignore)` / `expr.Raise(Rollback, msg)` (token singletons — `Rollback` reuses the existing top-level statement keyword; `expr.Ignore`/`expr.Abort`/`expr.Fail` are new). Three call styles supported pending future cleanup to a preferred form.

## Missing `literal-value` variants

Against the [`literal-value` grammar](https://sqlite.org/syntax/literal-value.html).

- [x] **Hexadecimal integer literals** — `0xFF` form — implemented as `HexLiteral(value)`, which validates non-negative and emits uppercase `0x<HEX>`. `IntLiteral` still emits decimal; reach for `HexLiteral` when hex notation is wanted.
- [x] **BLOB literals** — `X'53514C697465'` / `x'...'` — implemented as `BlobLiteral(bytes)`, also reachable via `literal(b"...")` since `bytes` has an unambiguous SQL form. Emits uppercase `X'<HEX>'`.

### Broken / limited (not strictly missing)

- [x] `StringLiteral` uses **double quotes** — fixed: now emits single-quoted form `'...'` and escapes embedded single quotes by doubling (`O'Reilly` → `'O''Reilly'`). Matches SQLite's literal-value grammar; identifier double-quoting (via `Name`) is unaffected.
- [x] `FloatLiteral` now rejects non-finite values (`inf`, `-inf`, `nan`) via `math.isfinite` at construction. Rendering still uses `str(float)`, which is bit-exact (shortest-roundtrip on IEEE 754 doubles) but flattens scientific notation (e.g. `1.5e10` → `15000000000.0`); users who need precise notation should use `NumericLiteral`.

## Other notes in the expression package

- [x] **Tcl-style `$` bind parameters** — `BindParameter("ns::var", "$")` and `BindParameter("var(idx)", "$")` now reach the looser `$` grammar per [SQLite docs](https://sqlite.org/lang_expr.html#varparam). Implemented in `bind_parameter.py` by splitting the named-style assertion: `$` accepts `identifier (::identifier)* (\(non-ws-non-paren*\))?` via a module-level compiled regex; `:` and `@` deliberately keep the existing strict `value.isalpha()` check (their own narrower grammars are out of scope for this entry).
