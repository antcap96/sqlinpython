# Files Still With Issues

_None — all files now rated Excellent on both criteria (or N/A)._

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
| `column_definition.py` | Excellent | Excellent | Fixed: `IPrimaryKeyConflict` mixin breaks `ColumnConstraintPrimaryKey(ColumnConstraintPrimaryKeyOrdered)` concrete chain; `IConflictClause` replaces concrete `ConflictClause` pass-through used by `WithNotNull`/`WithUnique` |
| `column_foreign_key_clause.py` | Excellent | Excellent | Fixed: `ColumnBeforeDeferrable` merged into `IColumnBeforeDeferrable`; ON and DEFERRABLE sub-chains inverted to terminal-at-top |
| `table_foreign_key_clause.py` | Excellent | Excellent | Fixed: `TableBeforeDeferrable` merged into `ITableBeforeDeferrable`; DEFERRABLE sub-chain moved above ON sub-chain |
| `select.py` | Excellent | Excellent | Fixed: concrete chain reordered and mixins interleaved — each `I*` mixin placed just above its first user; `SelectOrderBy` sits just below `ISelectLimit` |
| `common_table_expression.py` | Excellent | Excellent | Fixed: `IWithCall` mixin extracts `__call__` shared by `WithRecursive` and `WithKeyword`; both extend it directly |
| `expression/case.py` | Excellent | Excellent | Fixed: `IWhenCallable` mixin extracts `.When()` shared by `ThenClause`, `CaseWithBaseExpr`, and `CaseKeyword`; concrete chain broken |
| `create_view.py` | Excellent | Excellent | Fixed: `IHasAs` mixin extracts duplicated `.As()`; `ICallableCreateView` mixin extracts `__call__` — `CreateView` and `CreateViewIfNotExists` are now siblings |
| `create_table.py` | Excellent | Excellent | Fixed: `ITableOptions` mixin extracts `.WithoutRowId`/`.Strict`; `AddComma` removed; ordering validation + test added |
| `create_index.py` | Excellent | Excellent | Fixed: `ICallableCreateIndex` mixin extracts `__call__`; `CreateIndex` and `CreateIndexIfNotExists` are now siblings; bug removed where `CreateIndexIfNotExists` incorrectly exposed `.On()` |
| `drop.py` | Excellent | Excellent | Fixed: `IDropCallable[T]` mixin extracts duplicated `__call__` from `DropTypeKeyword` and `DropIfExists` |
| `type_name.py` | Excellent | Excellent | Fixed: `CompleteTypeName` made abstract; `TypeNameWithArgs` added as concrete "with numbers" variant |
| `alter_table.py` | Excellent | Excellent | Fixed: `IAlterTableOnConflict` mixin extracts shared `.OnConflict` from `AlterTableAddCheck` and `AlterTableAlterColumnSetNotNull`; `AlterTableAddConstraintCheck` moved above `AlterTableAddConstraintWithName` |
| `create.py` | Excellent | Excellent | Fixed: `ICreateTemp` and `ICreateUnique` mixins added; `CreateKeyword` extends both directly instead of the concrete classes; `__init__` smell resolved |
| `table_or_subquery.py` | Excellent | Excellent | Fixed: `Aliased(TableOrSubquery, ABC)` base unifies the three `*Aliased` classes; `explicit_as` extended to subquery/table-function per SQLite spec; `TableFunctionRef.__call__` narrowed to `Expression`; `TableStarResultColumn` lifted to top as a leaf helper |
| `indexed_column.py` | Excellent | Excellent | Fixed: `IndexedColumn` made abstract; `IHasAscDesc(IndexedColumn, IHasNulls, ABC)` mixin added; `ColumnNameWithOrdering` and `IndexedColumnWithCollate` are siblings extending it |
| `column_name.py` | Excellent | Excellent | Fixed: `IColumnNameAs(Expression, IColumnConstraint, ABC)` mixin extracts duplicated `Collate` and `As` from both `ColumnNameWithCollate` and `ColumnName`; `ColumnName` drops explicit `IColumnConstraint` base (encoded in mixin) |
| `insert.py` | Excellent | Excellent | Fixed: `IOnConflictDo`, `IBeforeUpsertClause`, `IInsertBody`, `ICallableWithColumnNames` mixins added; ordering corrected; `UpdateSet` API aligned with `Set` |
| `table_constraint.py` | Excellent | Excellent | Fixed: `TableConstraint` moved to top; `ConstraintBeforeConflictClause` changed to inherit `TableConstraint` directly (not via `TableConstraintWithConflictClause`); `ConstraintKeyword`/`Constraint` moved to bottom |
| `expression/core.py` | Excellent | Good | Fixed: `INegatedOperations` mixin extracts `Between`/`In`/`Glob`/`Regexp`/`Match`/`Like` shared by `Expression` and `NegatedOperator`; `IIsCallable` mixin breaks `IsExpression(IsNotExpression(IsDistinctFromExpression))` concrete chain into siblings; ordering follows precedence chain top→bottom (domain-specific exception) |
| `expression/function.py` | Excellent | Excellent | Fixed: `IFrameSpecBound` and `IFunctionCallOver` mixins added; `FunctionName` moved to bottom; `IHasFrameSpec`/`IHasOrderBy` mixin layer replaces concrete `PartitionByClause(OrderByClause)` and `WindowName(Name, PartitionByClause)` chains |
| `returning.py` | N/A | N/A | Single shared base class, no chain to evaluate |
| `select_base.py` | N/A | N/A | Type-tag markers and abstract base; infrastructure file |
| `conflict_clause.py` | N/A | N/A | Generic utility (`OnConflict_[T]`), not a builder chain |
| `ordering_term.py` | Excellent | Excellent | Fixed: `OrderingTerm` made pure type tag; `IHasNulls(OrderingTerm, ABC)` mixin added with `NullsFirst`/`NullsLast`; used by `IHasAscDesc` in `indexed_column.py` |
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

### `type_name.py` — Fixed

- `CompleteTypeName(SqlElement, ABC)` made abstract — it was concrete but only ever used as a type tag; per CLAUDE.md, the encoded base should itself be abstract.
- `TypeNameWithArgs(CompleteTypeName)` added as the concrete "with numbers" variant, holding `__init__` and `_create_query` (previously on `CompleteTypeName`).
- `TypeName(Name, CompleteTypeName)` now inherits from the abstract base; `__call__` return type narrowed to `TypeNameWithArgs`.

---

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

### `indexed_column.py` — Fixed

- `IndexedColumn(SqlElement, ABC)` made a pure abstract type tag; it was never directly instantiated.
- `IndexedColumnWithCollate` deleted — it was only ever used as a base class for `Expression` to inject `.Asc`/`.Desc`; with `IHasAscDesc` in place, it became dead code.
- `IHasNulls(OrderingTerm, ABC)` added to `ordering_term.py` — extracts `NullsFirst`/`NullsLast` that were duplicated across `ColumnNameWithOrdering` and `Expression`.
- `IHasAscDesc(IndexedColumn, IHasNulls, ABC)` added — encodes both `IndexedColumn` and `IHasNulls` (and thus `OrderingTerm`); provides `.Asc`/`.Desc`. `ColumnNameWithOrdering` extends it directly as the only concrete class.
- `ColumnNameWithOrdering(IHasAscDesc)` — concrete class; inherits all four methods (`Asc`, `Desc`, `NullsFirst`, `NullsLast`) plus both type relationships; holds only `__init__` and `_create_query`.
- `Expression(IHasAscDesc, ABC)` in `expression/core.py` — no longer depends on any concrete class; `NullsFirst`/`NullsLast` removed (inherited from `IHasNulls`); `OrderingTerm` import removed.

---

### `table_constraint.py` — Fixed

- `TableConstraint(SqlElement, ABC)` moved to the top of the file (was buried at line 143).
- `ConstraintBeforeConflictClause` changed to inherit `TableConstraint` directly instead of `TableConstraintWithConflictClause` — it overrides both `__init__` and `_create_query` so gained nothing from the concrete base, and is not conceptually a conflict-action result.
- `TableConstraintWithConflictClause` remains as the factory passed to `OnConflict_[T]`; `ConstraintBeforeConflictClause.OnConflict()` is unchanged.
- Terminal classes (`ConstraintBeforeConflictClause`, `CheckConstraint`) moved above mid-chain entries (`ForeignKeyConstraint`, `PrimaryKeyConstraint`, `UniqueConstraint`).
- `ConstraintWithName` and `ConstraintKeyword`/`Constraint` moved to the bottom as the branching hub and entry point.

---

### `column_name.py` — Fixed

- `IColumnNameAs(Expression, IColumnConstraint, ABC)` mixin added, extracting `Collate` and the overloaded `As` that were identically duplicated across `ColumnNameWithCollate` and `ColumnName`.
- `IColumnNameAs` listed first in both classes so its `Collate` and `As` win the MRO over `Expression.Collate`/`Expression.As` and `ColumnDefinition.Collate`/`ColumnDefinition.As`.
- `ColumnName` drops the explicit `IColumnConstraint` base — it is now encoded in the mixin (all implementors are always `IColumnConstraint`s).
- `ColumnNameWithCollate` body becomes empty; `ColumnName` retains only `__call__`.

---

### `alter_table.py` — Fixed

- `IAlterTableOnConflict(AlterTableStatement, ABC)` mixin added, extracting the `.OnConflict` property duplicated across `AlterTableAddCheck` and `AlterTableAlterColumnSetNotNull`; `AlterTableWithConflict` moved to sit just above the mixin instead of at the top of the file.
- `AlterTableAddConstraintCheck` moved above `AlterTableAddConstraintWithName`.

---

### `expression/core.py` — Fixed

- `INegatedOperations(SqlElement, ABC)` mixin added just above `Expression` (first user), extracting `Between`, `In` (with all overloads), `Glob`, `Regexp`, `Match`, `Like` shared between `Expression` and `NegatedOperator`. Each method uses an `isinstance(self, Expression)` check to decide whether to parenthesize `self` (needed for `Expression`) or pass it directly (correct for `NegatedOperator`). `NegatedOperator` retains `Null` (not shared with `Expression`).
- `IIsCallable(SqlElement, ABC)` mixin added just above `IsDistinctFromExpression`, providing `__call__(other) -> IsExpressionComplete`. `IsDistinctFromExpression`, `IsNotExpression`, and `IsExpression` are now siblings extending `IIsCallable` directly — the `IsExpression(IsNotExpression(IsDistinctFromExpression))` concrete chain is gone. `IsExpression.DistinctFrom` added explicitly (was previously inherited through the chain).
- `LikeExpression` changed from `LikeExpression(LikeExpressionWithEscape)` to `LikeExpression(Expression4)` — it completely overrides `__init__` and `_create_query`, so it only needed the `Expression4` type tag, not the concrete base.
- TODOs pruned: `bind-parameter`, `schema.table.column`, `function-call`, `Case` removed (all implemented); `tuple`, `cast`, `Exists`, `raise-function` remain.
- Ordering unchanged: precedence chain top→bottom is a domain-specific exception.

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

### `create_table.py` — Fixed

- `ITableOptions(CreateTableStatement, ABC)` mixin added, providing `.WithoutRowId` and `.Strict`; both `CreateTableWithDefinitions` and `CreateTableWithOptions` extend it directly.
- `AddComma` helper class removed — comma between chained table options is now handled by an `isinstance(self._prev, CreateTableWithOptions)` check in `CreateTableWithOptions._create_query`.
- `CreateTableWithDefinitions._create_query` simplified to use `comma_separated`.
- `CreateTableWithName.__call__` now validates that all `TableConstraint` items come after all `ColumnDefinition` items, raising `ValueError` otherwise; a corresponding test added.

---

### `expression/case.py` — Fixed

- `IWhenCallable(SqlElement, ABC)` mixin added, providing `.When(when) -> WhenClause`; the three independent `.When()` implementations on `ThenClause`, `CaseWithBaseExpr`, and `CaseKeyword` collapse into one.
- `CaseKeyword` no longer inherits from `CaseWithBaseExpr`; it extends `IWhenCallable` directly as a sibling.
- `IWhenCallable` placed just above `ThenClause` (the first user in file order).

---

### `column_definition.py` — Fixed (concrete-chain cleanup)

- `IPrimaryKeyConflict(ConflictClauseMaybeAutoIncrement, ABC)` mixin added — extracts `.OnConflict` previously defined on `ColumnConstraintPrimaryKeyOrdered`. `ColumnConstraintPrimaryKey` and `ColumnConstraintPrimaryKeyOrdered` now both extend the mixin directly as siblings; the previous `ColumnConstraintPrimaryKey(ColumnConstraintPrimaryKeyOrdered)` concrete inheritance only existed because the child overrode `__init__` AND `_create_query`, gaining nothing from the parent except `.OnConflict` and type-hierarchy placement.
- `IConflictClause(ConstraintWithClause, ABC)` replaces the concrete `ConflictClause` class — its body was a pass-through `_create_query` that did nothing, so the class was effectively abstract. `WithNotNull` and `WithUnique` now extend the mixin directly.

---

### `table_or_subquery.py` — Fixed

- `Aliased(TableOrSubquery, ABC)` base added, holding the shared `__init__(prev, alias, explicit_as)` and ` [AS] alias` render. `TableFunctionRefAliased` and `SubqueryAliased` collapse to empty subclasses; `TableRefAliased` extends it and adds `.Star`/`__getitem__` (the only behaviour that wasn't shared).
- `explicit_as: bool = True` kwarg added to `TableFunctionRefCall.As`, `Subquery.As`, and `ISelectAliasable.As` (`select.py`) — the optional `AS` is part of the SQLite grammar for all three forms, not just table-name refs. Tests added for each.
- `TableFunctionRef.__call__` and `TableFunctionRefCall._args` narrowed from `SqlElement` to `Expression` (table-function arguments are `expr` per the spec).
- `TableStarResultColumn` moved to the top of the file (just below imports) — it's a leaf helper, not a `TableOrSubquery`, so it no longer sits inside the chain hierarchy.

---

### `expression/function.py` — Fixed

- `IFrameSpecBound(WindowDefn, ABC)` replaces the concrete `FrameSpecBound(FrameSpecWithExclude)`: base changed from `FrameSpecWithExclude` to `WindowDefn` (frame bounds ARE valid window definitions, but are NOT themselves "frame specs with an EXCLUDE clause"); all four concrete frame bound classes now extend `IFrameSpecBound` directly; the `# type: ignore[assignment]` comments on `FrameSpecBetweenEnd` and `FrameSpecSingleBound` are removed (they were only needed due to the conflicting `_kind` Literal type from the old parent).
- `IFunctionCallOver(Expression13, ABC)` mixin added, providing `.Over()`; `FunctionCall` and `FunctionCallWithFilter` both extend it directly instead of chaining through each other.
- `FunctionName` moved to the bottom of the file — reading bottom-to-top now follows the builder chain: `FunctionName` → `FunctionCall` → `FunctionCallWithFilter` → `FunctionCallWithOver` (terminal).
- `IHasFrameSpec(WindowDefn, ABC)` mixin added providing `Range`/`Rows`/`Groups`; `IHasOrderBy(IHasFrameSpec, ABC)` mixin layered on top adds `OrderBy`. `OrderByClause(IHasFrameSpec)`, `PartitionByClause(IHasOrderBy)`, and `WindowName(Name, IHasOrderBy)` are now siblings — the previous concrete chains `PartitionByClause(OrderByClause)` and `WindowName(Name, PartitionByClause)` (both overrode `__init__` and `_create_query`, inheriting only the property accessors) are gone. CLAUDE.md's "Window function hierarchy" section updated to reflect the layered-mixin shape.
