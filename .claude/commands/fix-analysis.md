Apply code quality fixes from ANALYSIS.md to a source file, then update ANALYSIS.md and commit.

The argument is the file path relative to `src/sqlinpython/`, e.g. `/fix-analysis table_constraint.py`.

---

## Step 1 — Read the inputs

Read both files in parallel:
- `ANALYSIS.md` — find the row for the target file in the summary table and its detailed notes section
- `src/sqlinpython/<file>` — read the full current implementation

---

## Step 2 — Identify the issues

From the ANALYSIS.md notes, determine exactly what needs to change. The two criteria are:

**Mixin use** — shared behaviour should be in `I*` mixins; base classes encoded in the mixin when universal; concrete classes extend the mixin rather than chaining through concrete classes.

**Class ordering** — terminal states at top, entry point at bottom, abstract bases at very top, mixins placed just above the first concrete class that directly extends them (not grouped at top).

Present the required changes to the user using this format, then **wait for confirmation** before touching any file:

**Current structure** — annotated class list showing the problem (use `# comments` to highlight what's wrong):
```
ClassName(Base)          # problem description
```

**Proposed fix** — annotated class list showing the target state:
```
ClassName(NewBase)       # what changed and why
```

Follow the annotation with a short prose explanation of the structural issue (e.g. why the concrete chain exists only to share a method, or why a class is in the wrong position).

---

## Step 3 — Apply the fixes

Make the changes agreed in Step 2. Common patterns:

- **Merge a bridge class into its mixin**: if a file has both `ISomeMixin(SqlElement, ABC)` and `SomeBase(SharedBase, ISomeMixin, ABC)` where every user of `ISomeMixin` is always also a `SharedBase`, collapse them into `ISomeMixin(SharedBase, ABC)` and update all subclasses to extend `ISomeMixin` directly.

- **Reorder sub-chains by terminality**: a class that extends only `SharedBase` (no mixin methods remain) is more terminal than one that still extends a mixin. More terminal = higher in the file.

- **Move a mixin just above its first user**: find the first concrete class that directly extends the mixin; the mixin definition must sit immediately above it. If the mixin is a base class for many scattered classes, it must stay near the top (Python definition-order constraint).

- **Move the entry point to the bottom**: the class/singleton a user first touches belongs at the very bottom.

---

## Step 4 — Validate

```bash
just test
```

All 604 tests must pass. If any fail, fix them before continuing.

---

## Step 5 — Update ANALYSIS.md

Make two edits:

1. **Summary table row** — update the Mixin and Ordering ratings and the one-line verdict. If the file is now fully fixed, both ratings become `Excellent` and the verdict should start with `Fixed:`.

2. **Detailed notes section** — if the file had a `— Needs Work` or `— Good / Needs Work` heading, change it to `— Fixed` and replace or extend the bullet points with a concise description of what was done (mirror the style of the `insert.py — Fixed` entry).

---

## Step 6 — Commit

```bash
git add src/sqlinpython/<file> ANALYSIS.md
git commit
```

Write a commit message that describes the structural change (what was moved/merged and why), not just "apply ANALYSIS.md fixes". Look at recent commits on this branch for style reference.
