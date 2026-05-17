# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Test Commands

Use the `justfile` for common commands:

```bash
just test              # Run all tests
just test-one TEST     # Run specific test (e.g., just test-one tests/test_select.py::test_join)
just ty                # Type check with ty (primary type checker)
just pyright           # Type check with basedpyright
just mypy              # Type check with mypy
just types             # Run all three type checkers
just lint              # Check code style
just format            # Format code
just fix               # Fix code style issues
just check             # Full CI check: lint, types, and tests
```

## Type Ignore Comments

**Before adding any `# type: ignore` comment, you must ask me for approval.** Type ignores should be used sparingly and only when there's a legitimate reason that can't be fixed otherwise. Always investigate if there's a better solution first.

### Intentional type-error tests

Tests that verify a call is rejected by the type checkers use a bare expression statement (no `_ =` assignment — that triggers `reportUnknownVariableType`) with inline suppression for each checker:

```python
SomeClass().BadCall()  # type: ignore[error-code] # pyright: ignore[reportCode]
# ty doesn't currently identify this error -ty: ignore[ty-error-code]
```

`ty` often misses errors that mypy/pyright catch; leave the hypothetical ignore code in a comment.

Multi-line expected strings in assertions must use explicit `+` concatenation — basedpyright flags `reportImplicitStringConcatenation`:

```python
assert q.get_query() == (
    "WITH cte AS (SELECT 1) "
    + "UPDATE users SET column = 1"
)

## Architecture Overview

sqlinpython is a Python library that constructs SQL queries using type-annotated Python objects, providing editor autocompletion and static syntax checking. Queries are built using a chained-builder pattern and converted to SQL strings via `get_query()`.

### Core Base Classes (`base.py`)

- **`SqlElement`**: Abstract base class defining `_create_query(buffer: list[str]) -> None` interface. All SQL components inherit from this.
- **`CompleteSqlQuery(SqlElement)`**: Extends SqlElement with `get_query() -> str` for complete, executable queries.

### Expression System (`expression/`)

The expression system uses an **operator precedence hierarchy** (Expression1 through Expression13):

- `Expression1`: OR (lowest precedence)
- `Expression2`: AND
- `Expression3`: NOT
- `Expression4`: Comparison (=, !=, BETWEEN, IN, IS, LIKE, etc.)
- `Expression5`: Relational (<, >, <=, >=)
- `Expression7`: Bitwise (&, |, <<, >>)
- `Expression8`: Addition/Subtraction
- `Expression9`: Multiplication/Division
- `Expression10`: Concatenation (||)
- `Expression11`: COLLATE
- `Expression12`: Unary operators, bind parameters
- `Expression13`: Literals, function calls, parenthesized expressions (highest precedence)

The `_parenthesize_if_necessary()` function automatically wraps expressions in parentheses based on precedence.

### Interface/Mixin Naming Convention

Abstract mixin classes that provide shared methods use an `I` prefix and must inherit from `ABC` (basedpyright requires explicit abstractness to detect abstract classes):

```python
class IBeforeWhereClause(IBeforeReturningClause, ABC):
    def Where(self, condition: Expression) -> DeleteWhere: ...

class IIndexHints(IBeforeWhereClause, ABC):
    def IndexedBy(...) -> DeleteFromIndexedBy: ...
    def NotIndexed(...) -> DeleteFromNotIndexed: ...
```

**Encode the base class in the mixin when all implementors share it.** If every class that implements a mixin is always also a `ColumnDefinition`, put `ColumnDefinition` in the mixin's bases — not in every subclass. This removes repetition and makes the constraint explicit:

```python
class IColumnConstraint(ColumnDefinition, IColumnConstraintWithName, ABC):
    def Constraint(self, name: Name | str) -> ColumnConstraintWithName: ...

# result classes only need IColumnConstraint, not (ColumnDefinition, IColumnConstraint)
class WithCheck(IColumnConstraint): ...
class WithDefault(IColumnConstraint): ...
```

**But** only do this when it is truly universal. `IColumnConstraintWithName` is also implemented by `ColumnConstraintWithName` (the result of `.Constraint("name")`), which is NOT a `ColumnDefinition` on its own — so `ColumnDefinition` belongs on `IColumnConstraint`, not `IColumnConstraintWithName`.

### Method Ordering Convention

In all `SqlElement` subclasses, methods must follow this order:
1. `__init__` — always first
2. Other methods/properties (in any order)
3. `_create_query` — always last

### Class Ordering Convention

Within a module, classes are ordered so that **reading bottom-to-top follows the builder chain**: the entry point (or closest class to the entry point) sits at the bottom, and terminal states sit at the top. Abstract bases and mixins must be defined before the classes that use them, so they appear near the top regardless.

```
# top — abstract bases and mixins (must come first for inheritance)
class ColumnDefinition(SqlElement, ABC): ...
class IColumnConstraint(ColumnDefinition, ...): ...

# middle — terminal states (deepest in the chain)
class ConflictClauseAutoIncrement(IColumnConstraint): ...
class WithNotNull(ConflictClause): ...

# bottom — entry point (first class a user touches)
class ColumnNameWithType(IColumnConstraint): ...
```

### Chained Builder Pattern

Statements are built through fluent method chaining where each stage returns a new builder instance:

```python
Create.Table("users")(
    ColumnName("id")(TypeName("INT")),
    ColumnName("name")(TypeName("TEXT"))
).WithoutRowId.get_query()
```

Each builder class:
1. Stores reference to previous stage
2. Implements `_create_query()` that calls previous stage's method then appends its portion
3. Returns next stage from its methods/properties

Entry points are singleton instances: `Create`, `Case`, `Not`, `Insert`, `Replace`, `With`, etc.

### Key Modules

- `expression/core.py`: Expression hierarchy with operator overloading
- `expression/literal.py`: SQL literals (INT, FLOAT, STRING, BOOL, NULL)
- `expression/case.py`: CASE/WHEN/THEN/ELSE/END builder
- `expression/bind_parameter.py`: Parameter binding (?, :name, $name, @name)
- `expression/function.py`: Function calls, window functions, frame specs
- `ordering_term.py`: ORDER BY terms with NULLS FIRST/LAST support
- `name.py`: Identifier handling with automatic quoting
- `create.py`, `create_table.py`, `create_index.py`: CREATE statement builders
- `column_definition.py`: Column specifications and column-constraint mixins
- `column_name.py`: `ColumnName` and `col()` helper
- `column_foreign_key_clause.py`: Column-level FK clause chain (produces `ColumnDefinition`)
- `table_constraint.py`: Table-level constraints
- `table_foreign_key_clause.py`: Table-level FK clause chain (produces `TableConstraint`)
- `common_table_expression.py`: CTEs and WITH clause
- `insert.py`: INSERT/REPLACE statements with upsert and RETURNING

### Query Generation Flow

1. Build chain of objects via fluent API
2. Call `get_query()` which creates empty buffer
3. Each `_create_query()` recursively calls previous stage then appends its SQL fragment
4. Buffer joined into final SQL string

### Testing Pattern

Tests for incomplete `SqlElement` objects use a `to_str(element: SqlElement)` helper that manually invokes `_create_query()` to get string representation.

### Function Calls and Window Functions (`expression/function.py`)

Function calls support the full SQLite syntax:
```python
FunctionName("COUNT")("*")                    # COUNT(*)
FunctionName("SUM")(a).FilterWhere(cond)      # SUM(a) FILTER (WHERE cond)
FunctionName("SUM")(a).Over(PartitionBy(b))   # SUM(a) OVER (PARTITION BY b)
```

**Window function hierarchy:**
- `WindowDefn` → base class for window definitions
- `OrderByClause` → has `Range`, `Rows`, `Groups` properties
- `PartitionByClause(OrderByClause)` → inherits frame spec access, has `OrderBy`
- `WindowName(Name, PartitionByClause)` → inherits both PARTITION BY and frame spec

**Frame spec pattern** uses chained properties/calls:
```python
Rows.CurrentRow                                    # ROWS CURRENT ROW
Rows.UnboundedPreceding                            # ROWS UNBOUNDED PRECEDING
Rows(a.Preceding)                                  # ROWS 1 PRECEDING
Rows.Between.UnboundedPreceding.And.CurrentRow     # ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
Rows.Between(a.Preceding).And(b.Following)         # ROWS BETWEEN 1 PRECEDING AND 2 FOLLOWING
Rows.CurrentRow.ExcludeTies                        # ROWS CURRENT ROW EXCLUDE TIES
```

**Key patterns learned:**
1. Use `Literal` types to differentiate similar keywords (e.g., `Literal["RANGE", "ROWS", "GROUPS"]`)
2. Use `# type: ignore[assignment]` when subclasses reuse attribute names with different Literal types
3. Inheritance can share properties across related clauses (e.g., `PartitionByClause` inherits from `OrderByClause` to get `Range`/`Rows`/`Groups`)
4. Expression properties like `expr.Preceding` and `expr.Following` create frame bound objects

### Common Table Expressions (`common_table_expression.py`)

CTEs and WITH clause support:
```python
With(cte1, cte2)                    # WITH cte1, cte2
With.Recursive(cte1, cte2)          # WITH RECURSIVE cte1, cte2
TableName("t1").As(select_stmt)     # t1 AS (select-stmt)
TableName("t1")("a", "b").As(...)   # t1(a, b) AS (...)
TableName("t1").As.Materialized(...) # t1 AS MATERIALIZED (...)
TableName("t1").As.Not.Materialized(...) # t1 AS NOT MATERIALIZED (...)
```

**Key patterns:**
1. Use `NotImplementedSqlElement` subclasses (e.g., `SelectStatement`) as placeholders for unimplemented syntax - allows type checking and easy identification of TODOs
2. Trailing underscore in class names (e.g., `As_`, `CteNot_`) only when a property has the same name as the class it returns
3. Use inheritance to share `__call__` methods (e.g., `WithKeyword(WithRecursive)` inherits `__call__` instead of duplicating)
4. Entry point classes take no `__init__` args and are instantiated as singletons (e.g., `With = WithKeyword()`)
5. Multi-inheritance for classes that need properties from multiple paths (e.g., `TableName(Name, CteTableNameWithColumns)`)

### INSERT Statement (`insert.py`)

INSERT and REPLACE statement support:
```python
Insert.Into("table")("col1", "col2").Values((a, b), (c, d))  # INSERT INTO table(col1, col2) VALUES (a, b), (c, d)
Insert.Into("table").DefaultValues                            # INSERT INTO table DEFAULT VALUES
Insert.Or.Replace.Into("table")("col").Values((a,))          # INSERT OR REPLACE INTO table(col) VALUES (a)
Replace.Into("table")("col").Values((a,))                     # REPLACE INTO table(col) VALUES (a)
With(cte).Insert.Into("table")...                             # WITH cte INSERT INTO table...
```

**Upsert (ON CONFLICT) clause:**
```python
.OnConflict.Do.Nothing                                        # ON CONFLICT DO NOTHING
.OnConflict(col.Asc).Do.Nothing                               # ON CONFLICT(col ASC) DO NOTHING
.OnConflict(col).Where(cond).Do.Nothing                       # ON CONFLICT(col) WHERE cond DO NOTHING
.OnConflict.Do.UpdateSet(("col", expr))                       # ON CONFLICT DO UPDATE SET col = expr
.OnConflict.Do.UpdateSet((("c1", "c2"), expr))                # ON CONFLICT DO UPDATE SET (c1, c2) = expr
.OnConflict.Do.UpdateSet(("col", expr)).Where(cond)           # ... WHERE cond
```

**RETURNING clause:**
```python
.Returning("*")                                               # RETURNING *
.Returning(col1, col2)                                        # RETURNING col1, col2
.Returning(col.As("alias"))                                   # RETURNING col AS alias
```

**Key patterns:**
1. Entry point singleton classes use `*Keyword` suffix (e.g., `InsertKeyword`, `ReplaceKeyword`)
2. Use `@typing.overload` for methods accepting different argument types (e.g., `ColumnName.As` handles both aliasing and generated column expressions)
3. `AliasedExpression` class in `expression/core.py` handles `expr AS alias` syntax

### Parallel chains: two files over generics

When two chains are structurally identical but rooted in different base classes (e.g. column FK vs table FK), prefer **two separate files** over a generic abstraction. Generics require abstract bound classes and type parameter syntax that add complexity without improving readability. Duplication across two small files is cheaper than the indirection:

```
# column_foreign_key_clause.py  — inherits ColumnDefinition
class ColumnReferences_(ColumnBeforeDeferrable): ...

# table_foreign_key_clause.py   — inherits TableConstraint
class TableReferences_(TableBeforeDeferrable): ...
```

This also enforces correct type separation at no extra cost — a `TableReferences_` cannot be used where a `ColumnDefinition` is expected.

### Statement / statement-limited pairs (`update.py`)

When a statement has a "limited" variant (e.g. `update-stmt` / `update-stmt-limited`), the plain base class extends the limited one — not the other way around:

```python
class UpdateStatementLimited(CompleteSqlQuery, ABC): ...  # ORDER BY / LIMIT results
class UpdateStatement(UpdateStatementLimited, ABC): ...   # plain UPDATE results
```

This means any plain UPDATE result satisfies `isinstance(q, UpdateStatementLimited)` (Liskov: a plain UPDATE is always valid wherever a limited UPDATE is accepted). The ORDER BY / LIMIT result classes only extend the limited base, not the plain one. Apply this pattern for any future stmt / stmt-limited pair (e.g. `delete-stmt-limited`).
