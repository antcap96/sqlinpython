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
| `column_definition.py` | Excellent | Good | `IColumnConstraint`/`IColumnConstraintWithName` split is the canonical pattern; minor: `ConstraintWithClause` not marked `ABC` |
| `column_foreign_key_clause.py` | Excellent | Needs Work | `IColumnBeforeDeferrable`/`ColumnBeforeDeferrable` split clean; inner sub-chains ordered top→bottom instead of bottom→top |
| `table_foreign_key_clause.py` | Excellent | Needs Work | Identical to column FK — same strengths and the same ordering issue |
| `select.py` | Excellent | Needs Work | Eight generic `I*` mixins; concrete chain (`SelectColumns`→…→`SelectValues`) is ordered entry-first instead of entry-last |
| `common_table_expression.py` | Good | Excellent | No `I*` mixins needed (chain too short); concrete inheritance reuse is appropriate; ordering perfect |
| `expression/case.py` | Good | Excellent | `CaseKeyword(CaseWithBaseExpr)` for `.When()` reuse; perfect terminal-at-top ordering |
| `create_view.py` | Good | Excellent | Minor: `.As()` duplicated in `CreateViewWithColumns` and `CreateViewWithName` — a one-method `IHasAs` mixin would remove it |
| `create_table.py` | Good | Excellent | `.WithoutRowId`/`.Strict` duplicated across `CreateTableWithDefinitions` and `CreateTableWithOptions`; otherwise clean |
| `create_index.py` | Good | Excellent | Short, linear chain; `CreateIndex(CreateIndexIfNotExists)` reuse pattern correct |
| `drop.py` | Good | Excellent | Generics used effectively for the four DROP variants; clean ordering |
| `type_name.py` | Good | Excellent | `TypeName(Name, CompleteTypeName)` inherits `__call__` reuse; two-class file, correct ordering |
| `alter_table.py` | Good | Good | `IAlterTableRenameColumnTo` and `IAlterTableAlterColumn` well-placed; one ordering issue in ADD section (see detail) |
| `create.py` | Good | Good | `CreateKeyword(CreateTempTable, CreateUnique)` multiple inheritance to share `.Table`/`.Index`/etc. without duplication; `__init__` doesn't call `super().__init__` which is a minor smell |
| `table_or_subquery.py` | Good | Good | All JOIN methods in `TableOrSubquery` base class (appropriate — every subclass needs them); each sub-chain (`TableRef`, `TableFunctionRef`, `Subquery`, join) correctly ordered internally |
| `indexed_column.py` | Good | Good | `IndexedColumnWithCollate` (produces `ColumnNameWithOrdering`) correctly sits below it in the file |
| `column_name.py` | Good | Good | `ColumnNameWithCollate` bridges expression and column-def worlds via multiple inheritance; `ColumnName` multi-inheritance is necessary; ordering correct |
| `insert.py` | Excellent | Excellent | Fixed: `IOnConflictDo`, `IBeforeUpsertClause`, `IInsertBody`, `ICallableWithColumnNames` mixins added; ordering corrected; `UpdateSet` API aligned with `Set` |
| `table_constraint.py` | Good | Needs Work | No `I*` mixins; `TableConstraint` (abstract base) buried at line 143 instead of at top; `ConstraintKeyword` (entry) at line 16 instead of bottom |
| `expression/core.py` | Needs Work | Good | `NegatedOperator` duplicates ~8 methods from `Expression`; `IsExpression` chain uses concrete→concrete inheritance (same anti-pattern as `insert.py`); ordering follows precedence chain top→bottom which is reasonable for this domain |
| `expression/function.py` | Good | Needs Work | `FunctionCall→FunctionCallWithFilter→FunctionCallWithOver` concrete chain is acceptable; `FunctionName` (entry) at line 27 instead of near the bottom |
| `returning.py` | N/A | N/A | Single shared base class, no chain to evaluate |
| `select_base.py` | N/A | N/A | Type-tag markers and abstract base; infrastructure file |
| `conflict_clause.py` | N/A | N/A | Generic utility (`OnConflict_[T]`), not a builder chain |
| `ordering_term.py` | N/A | N/A | Two-class leaf file |
| `expression/literal.py` | N/A | N/A | Flat leaf types, no chain |
| `name.py` | N/A | N/A | Foundation class |
| `base.py` | N/A | N/A | Foundation class |
| Simple stmts | N/A | N/A | `analyze.py`, `attach.py`, `detach.py`, `pragma.py`, `reindex.py`, `savepoint.py`, `transaction.py`, `vacuum.py` — single-class or two-class files |
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

### `select.py` — Excellent / Needs Work

**Ordering issue only.**

The eight `I*` mixins form a dependency chain (`ISelectFromClause → ISelectWhereClause → … → ISelectLimit`), which means they must be defined together in dependency order before any concrete class that uses them. Grouping them is therefore correct.

The problem is the concrete classes block (lines 173–328): `SelectColumns` sits at the TOP of that block, but it is the FIRST result in the chain (produced directly by `SelectKeyword`), so it should be at the BOTTOM of the block, just above the entry keywords. The current order reads top-to-bottom as the builder chain, which is the opposite of the CLAUDE.md convention.

Correct order for the concrete block (top → bottom):
```
SelectValues / SelectCompound   # most terminal
SelectOrderBy
SelectWindowClause
SelectHavingClause
SelectGroupByClause
SelectWhereClause
SelectFromClause
SelectColumns                   # closest to entry — goes just above SelectKeyword
```

---

### `column_foreign_key_clause.py` / `table_foreign_key_clause.py` — Excellent / Needs Work

**Ordering issue only (identical in both files).**

`ColumnForeignKeyClause`, `IColumnBeforeDeferrable`, and `ColumnBeforeDeferrable` are correctly at the top as abstract bases inherited throughout the chain.

Within the mid-chain section, each sub-chain is ordered top-to-bottom (reading down follows the chain) instead of bottom-to-top. For example:

```
# Current order (WRONG)
ColumnOn_          # produced by IColumnBeforeDeferrable.On
ColumnOnAction_    # produced by ColumnOn_.Delete / .Update
ColumnOnActionDo   # terminal

# Correct order
ColumnOnActionDo   # terminal — at top
ColumnOnAction_    # one step from terminal
ColumnOn_          # entry of this sub-chain — at bottom
```

The same inversion applies to `ColumnDeferrable_ → ColumnInitially_ → ColumnInitiallyHow`. The outermost ordering (abstract base at top, `ColumnReferences_` entry at bottom) is correct.

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

### `alter_table.py` — Good / Good

One ordering issue in the ADD section: `AlterTableAddConstraintCheck` (terminal, produced by `AlterTableAddConstraintWithName.Check()`) sits below `AlterTableAddConstraintWithName` — it should be above it.

---

### `expression/core.py` — Needs Work / Good

**Mixin issue:**

`NegatedOperator` (line 586) re-implements `Between`, `In`, `Glob`, `Regexp`, `Match`, `Like`, and `Null` — nearly the same set of methods as `Expression`. An `INegatedOperations` mixin would let both `Expression` and `NegatedOperator` share these without duplication.

`IsExpression(IsNotExpression(IsDistinctFromExpression))` is concrete-to-concrete inheritance to share `__call__` — the same anti-pattern as `insert.py`'s upsert chain.

**Ordering:** The precedence chain ordered lowest-to-highest (`Expression1` OR → `Expression13` literals) reads naturally top-to-bottom, which is the reverse of the CLAUDE.md convention but is a reasonable domain-specific exception.

---

### `expression/function.py` — Good / Needs Work

**Ordering issue only.**

`FunctionName` (line 27) is the entry point for function calls — calling it produces `FunctionCall`. It should be near the bottom of the file, just above the entry singletons `Range`, `Rows`, `Groups`, `PartitionBy`. Currently it sits near the very top, above the entire frame-spec and window-definition machinery that it sits logically "before" in the chain.
