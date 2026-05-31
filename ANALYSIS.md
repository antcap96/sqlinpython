# Files Still With Issues

## Needs Work

| File | Mixins | Ordering |
|------|--------|----------|
| `table_constraint.py` | Good | Needs Work |
| `expression/core.py` | Needs Work | Good |

## Good (no Needs Work)

| File | Mixins | Ordering |
|------|--------|----------|
| `expression/case.py` | Good | Excellent |
| `create_table.py` | Good | Excellent |
| `type_name.py` | Good | Excellent |
| `table_or_subquery.py` | Good | Good |
| `indexed_column.py` | Good | Good |
| `column_name.py` | Good | Good |

---

# Code Quality Analysis

Two criteria per file, per CLAUDE.md conventions:

- **Mixin use** — Shared behaviour extracted into `I*` mixins? Base classes encoded in the mixin when universal? Concrete classes each extend exactly one mixin?
- **Class ordering** — Entry point at bottom, terminal states at top? Mixins placed just above first user? Abstract bases at very top?

Ratings: **Excellent** / **Good** / **Needs Work** / **N/A**

---

## Summary Table

| File | Mixins | Ordering | One-line verdict |
|------|--------|----------|-----------------|
| `delete.py` | Excellent | Excellent | Textbook — five `I*` mixins, each placed just above first user |
| `update.py` | Excellent | Excellent | Same discipline as `delete.py` |
| `create_trigger.py` | Excellent | Excellent | Four `I*` mixins (`IBeforeBegin`, `IWithWhen`, `IBeforeOnTable`, `IEventClause`), all correctly placed |
| `column_definition.py` | Excellent | Excellent | Fixed: `ConstraintWithClause` marked `ABC`; `IColumnConstraint`/`IColumnConstraintWithName` split is the canonical pattern |
| `column_foreign_key_clause.py` | Excellent | Excellent | Fixed: `ColumnBeforeDeferrable` merged into `IColumnBeforeDeferrable`; ON and DEFERRABLE sub-chains inverted to terminal-at-top |
| `table_foreign_key_clause.py` | Excellent | Excellent | Fixed: `TableBeforeDeferrable` merged into `ITableBeforeDeferrable`; DEFERRABLE sub-chain moved above ON sub-chain |
| `select.py` | Excellent | Excellent | Fixed: concrete chain reordered and mixins interleaved — each `I*` mixin placed just above its first user; `SelectOrderBy` sits just below `ISelectLimit` |
| `common_table_expression.py` | Excellent | Excellent | Fixed: `IWithCall` mixin extracts `__call__` shared by `WithRecursive` and `WithKeyword`; both extend it directly |
| `expression/case.py` | Good | Excellent | `CaseKeyword(CaseWithBaseExpr)` for `.When()` reuse; perfect terminal-at-top ordering |
| `create_view.py` | Excellent | Excellent | Fixed: `IHasAs` mixin extracts duplicated `.As()`; `ICallableCreateView` mixin extracts `__call__` — `CreateView` and `CreateViewIfNotExists` are now siblings |
| `create_table.py` | Good | Excellent | `.WithoutRowId`/`.Strict` duplicated across `CreateTableWithDefinitions` and `CreateTableWithOptions`; otherwise clean |
| `create_index.py` | Excellent | Excellent | Fixed: `ICallableCreateIndex` mixin extracts `__call__`; `CreateIndex` and `CreateIndexIfNotExists` are now siblings; bug removed where `CreateIndexIfNotExists` incorrectly exposed `.On()` |
| `drop.py` | Excellent | Excellent | Fixed: `IDropCallable[T]` mixin extracts duplicated `__call__` from `DropTypeKeyword` and `DropIfExists` |
| `type_name.py` | Good | Excellent | `TypeName(Name, CompleteTypeName)` inherits `__call__` reuse; two-class file, correct ordering |
| `alter_table.py` | Excellent | Excellent | Fixed: `IAlterTableOnConflict` mixin extracts shared `.OnConflict` from `AlterTableAddCheck` and `AlterTableAlterColumnSetNotNull`; `AlterTableAddConstraintCheck` moved above `AlterTableAddConstraintWithName` |
| `create.py` | Excellent | Excellent | Fixed: `ICreateTemp` and `ICreateUnique` mixins added; `CreateKeyword` extends both directly instead of the concrete classes; `__init__` smell resolved |
| `table_or_subquery.py` | Good | Good | All JOIN methods in `TableOrSubquery` base class (appropriate — every subclass needs them); each sub-chain (`TableRef`, `TableFunctionRef`, `Subquery`, join) correctly ordered internally |
| `indexed_column.py` | Good | Good | `IndexedColumnWithCollate` (produces `ColumnNameWithOrdering`) correctly sits below it in the file |
| `column_name.py` | Good | Good | `ColumnNameWithCollate` bridges expression and column-def worlds via multiple inheritance; `ColumnName` multi-inheritance is necessary; ordering correct |
| `insert.py` | Excellent | Excellent | Fixed: `IOnConflictDo`, `IBeforeUpsertClause`, `IInsertBody`, `ICallableWithColumnNames` mixins added; ordering corrected; `UpdateSet` API aligned with `Set` |
| `table_constraint.py` | Good | Needs Work | No `I*` mixins; `TableConstraint` (abstract base) buried at line 143 instead of at top; `ConstraintKeyword` (entry) at line 16 instead of bottom |
| `expression/core.py` | Needs Work | Good | `NegatedOperator` duplicates ~8 methods from `Expression`; `IsExpression` chain uses concrete→concrete inheritance (same anti-pattern as `insert.py`); ordering follows precedence chain top→bottom which is reasonable for this domain |
| `expression/function.py` | Excellent | Excellent | Fixed: `IFrameSpecBound` and `IFunctionCallOver` mixins added; `FunctionName` moved to bottom |
| `returning.py` | N/A | N/A | Single shared base class, no chain to evaluate |
| `select_base.py` | N/A | N/A | Type-tag markers and abstract base; infrastructure file |
| `conflict_clause.py` | N/A | N/A | Generic utility (`OnConflict_[T]`), not a builder chain |
| `ordering_term.py` | N/A | N/A | Two-class leaf file |
| `expression/literal.py` | N/A | N/A | Flat leaf types, no chain |
| `name.py` | N/A | N/A | Foundation class |
| `base.py` | N/A | N/A | Foundation class |
| `analyze.py` | N/A | N/A | Single entry + single result; no chain to evaluate |
| `attach.py` | Excellent | N/A | `IAttachCall` mixin correctly shared by `AttachKeyword` and `AttachDatabaseKeyword` |
| `detach.py` | Excellent | N/A | `IDetachCall` mixin correctly shared by `DetachKeyword` and `DetachDatabaseKeyword` |
| `pragma.py` | N/A | N/A | Linear two-class chain; no shared behaviour |
| `reindex.py` | N/A | N/A | All methods on the single entry class; no inheritance chain |
| `savepoint.py` | Excellent | N/A | Fixed: `ICallableReleaseSavepoint`, `ICallableRollbackSavepoint`, `IRollbackWithTo` mixins added; all three concrete chains broken |
| `transaction.py` | Excellent | N/A | Fixed: `IBeginTransaction`/`ICommitTransaction` encode `BeginStatement`/`CommitStatement`; concrete base removed from all four keyword classes |
| `vacuum.py` | Excellent | N/A | Fixed: `IVacuumInto(VacuumStatement, ABC)` mixin added; `VacuumKeyword` and `VacuumWithSchema` now both extend it directly |
| `builders.py`, `keywords.py`, `types.py` | N/A | N/A | Utilities / re-export files |

---

## Detailed Notes for Files with Issues

### `insert.py` — Fixed

All mixin and ordering issues resolved:

- `IOnConflictDo(SqlElement, ABC)` replaces the `OnConflictClause → OnConflictCall → OnConflictWhere` concrete chain; `.Where()` leak removed.
- `OnConflictDoUpdateSet` extends `IBeforeReturningClause` directly.
- `BeforeUpsertClause` renamed to `IBeforeUpsertClause`.
- `IInsertBody(SqlElement, ABC)` extracts `Values`, `__call__` (select), and `DefaultValues` from `InsertColumnNames`.
- `ICallableWithColumnNames(IInsertBody, ABC)` extracts the overloaded `__call__` that dispatches between column names and `SelectStatement`; `InsertNameAs` and `IntoName` both extend it directly instead of using concrete-to-concrete inheritance.
- `UpdateSet` API aligned with `Set` in `update.py`: dict + `**kwargs`, uses `Name` throughout, validates non-empty.
- Class ordering corrected: terminals at top, entry chain at bottom, each mixin placed just above its first user.

---

### `select.py` — Fixed

- Concrete chain reordered to terminal-at-top.
- Mixins interleaved: each `I*` mixin placed just above its first user. `ISelectLimit`, `ISelectOrderBy`, and `ISelectCompound` must stay grouped (they form a dependency chain needed before the first concrete class `SelectValues`); the remaining five (`ISelectWindowClause` → `ISelectFromClause`) each sit just above their first concrete user.
- `SelectOrderBy` moved above `ISelectOrderBy` (it is a concrete result class, not a mixin) and sits just below `ISelectLimit` (which it directly extends).

---

### `column_foreign_key_clause.py` — Fixed

- `ColumnBeforeDeferrable` merged into `IColumnBeforeDeferrable(ColumnForeignKeyClause, ABC)` (no independent users; encodes the shared base per CLAUDE.md convention).
- DEFERRABLE sub-chain (`ColumnInitiallyHow`, `ColumnInitially_`, `ColumnDeferrable_`, `ColumnNot_`) placed above the ON sub-chain and `ColumnMatch_` — these classes extend `ColumnForeignKeyClause` directly (true terminals), whereas `ColumnOnActionDo` and `ColumnMatch_` extend `IColumnBeforeDeferrable` (less terminal).
- ON sub-chain inverted to `ColumnOnActionDo`, `ColumnOnAction_`, `ColumnOn_` and placed below DEFERRABLE sub-chain.
- Final order: `ColumnForeignKeyClause` → DEFERRABLE sub-chain → `IColumnBeforeDeferrable` → ON sub-chain → `ColumnMatch_` → `ColumnReferenceWithColumns` → `ColumnReferences_` (entry).

### `table_foreign_key_clause.py` — Fixed

- `ITableBeforeDeferrable(SqlElement, ABC)` + `TableBeforeDeferrable(TableForeignKeyClause, ITableBeforeDeferrable, ABC)` merged into `ITableBeforeDeferrable(TableForeignKeyClause, ABC)` (same fix as column FK).
- DEFERRABLE sub-chain (`TableInitiallyHow`, `TableInitially_`, `TableDeferrable_`, `TableNot_`) placed above ON sub-chain and `TableMatch_` — true terminals extending `TableForeignKeyClause` directly.
- `ITableBeforeDeferrable` mixin placed just above its first user (`TableOnActionDo`).

---

### `table_constraint.py` — Good / Needs Work

**Ordering issue only.**

`TableConstraint` (the abstract base that `ConstraintBeforeConflictClause`, `CheckConstraint`, and `TableForeignKeyClause` all inherit from) is defined at line 143, well below `PrimaryKeyConstraint` (line 95), `UniqueConstraint` (line 124), `ConstraintWithName` (line 30), and `ConstraintKeyword` (line 16). Python allows this because none of those earlier classes inherit from `TableConstraint`, but it violates the "abstract base at the top" rule.

`ConstraintKeyword` and its singleton `Constraint = ConstraintKeyword()` are the entry points and should be at the bottom.

Correct file structure:
```
TableConstraint                          # abstract base — very top
TableConstraintWithConflictClause
ConstraintBeforeConflictClause           # terminal
CheckConstraint                          # terminal
ForeignKeyConstraint                     # entry for FK sub-chain
PrimaryKeyConstraint                     # entry for PK sub-chain
UniqueConstraint                         # entry for UNIQUE sub-chain
ConstraintWithName                       # branches to all of the above
ConstraintKeyword / Constraint           # entry — bottom
```

---

### `alter_table.py` — Fixed

- `IAlterTableOnConflict(AlterTableStatement, ABC)` mixin added, extracting the `.OnConflict` property duplicated across `AlterTableAddCheck` and `AlterTableAlterColumnSetNotNull`; `AlterTableWithConflict` moved to sit just above the mixin instead of at the top of the file.
- `AlterTableAddConstraintCheck` moved above `AlterTableAddConstraintWithName`.

---

### `expression/core.py` — Needs Work / Good

**Mixin issue:**

`NegatedOperator` (line 586) re-implements `Between`, `In`, `Glob`, `Regexp`, `Match`, `Like`, and `Null` — nearly the same set of methods as `Expression`. An `INegatedOperations` mixin would let both `Expression` and `NegatedOperator` share these without duplication.

`IsExpression(IsNotExpression(IsDistinctFromExpression))` is concrete-to-concrete inheritance to share `__call__` — the same anti-pattern as `insert.py`'s upsert chain.

**Ordering:** The precedence chain ordered lowest-to-highest (`Expression1` OR → `Expression13` literals) reads naturally top-to-bottom, which is the reverse of the CLAUDE.md convention but is a reasonable domain-specific exception.

---

### `savepoint.py` — Fixed

- `ICallableReleaseSavepoint(SqlElement, ABC)` extracts `__call__(savepoint) -> ReleaseComplete` shared by `ReleaseWithSavepoint` and `ReleaseKeyword`; both now extend the mixin directly as siblings.
- `ICallableRollbackSavepoint(SqlElement, ABC)` extracts `__call__(savepoint) -> RollbackComplete` shared by `RollbackWithToSavepoint` and `RollbackWithTo`; both now extend the mixin directly as siblings.
- `IRollbackWithTo(RollbackStatement, ABC)` extracts `.To -> RollbackWithTo`; `RollbackWithTransaction` no longer inherits the terminal `RollbackComplete` (it was only doing so to land in `RollbackStatement`'s hierarchy); `RollbackKeyword` no longer inherits `RollbackWithTransaction`. Both become `RollbackStatement` instances via the mixin — correct, since `ROLLBACK` and `ROLLBACK TRANSACTION` are both valid complete SQL.

---

### `transaction.py` — Fixed

- `IBeginTransaction(BeginStatement, ABC)` now encodes `BeginStatement`; `BeginWithType` and `BeginKeyword` extend it directly, dropping the redundant `BeginWithTransaction` base.
- `ICommitTransaction(CommitStatement, ABC)` now encodes `CommitStatement`; `CommitKeyword` and `EndKeyword` extend it directly, dropping the redundant `CommitWithTransaction` base.

---

### `vacuum.py` — Fixed

- `IVacuumInto(VacuumStatement, ABC)` mixin added, providing `.Into() -> VacuumWithIntoFileName`.
- `VacuumWithSchema` and `VacuumKeyword` now both extend `IVacuumInto` directly; neither inherits the other.
- `VacuumWithSchema` no longer inherits the terminal `VacuumWithIntoFileName` — the concrete chain is gone.

---

### `expression/function.py` — Fixed

- `IFrameSpecBound(WindowDefn, ABC)` replaces the concrete `FrameSpecBound(FrameSpecWithExclude)`: base changed from `FrameSpecWithExclude` to `WindowDefn` (frame bounds ARE valid window definitions, but are NOT themselves "frame specs with an EXCLUDE clause"); all four concrete frame bound classes now extend `IFrameSpecBound` directly; the `# type: ignore[assignment]` comments on `FrameSpecBetweenEnd` and `FrameSpecSingleBound` are removed (they were only needed due to the conflicting `_kind` Literal type from the old parent).
- `IFunctionCallOver(Expression13, ABC)` mixin added, providing `.Over()`; `FunctionCall` and `FunctionCallWithFilter` both extend it directly instead of chaining through each other.
- `FunctionName` moved to the bottom of the file — reading bottom-to-top now follows the builder chain: `FunctionName` → `FunctionCall` → `FunctionCallWithFilter` → `FunctionCallWithOver` (terminal).
