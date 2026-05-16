Implement a new SQL statement for sqlinpython following the standard feature workflow.

The argument (if provided) is the statement name, e.g. `/implement-stmt analyze` works on `analyze-stmt`.

---

## Step 1 — Create branch

```bash
git checkout main && git checkout -b feature/<stmt>-stmt
```

---

## Step 2 — Audit the test file

Read `tests/test_<stmt>.py`. Check for:
- Missing SQL keywords in expected strings (e.g. `== "name"` instead of `== "ANALYZE name"`)
- Missing `-> None` return type annotations on test functions
- Missing edge cases (no-arg form, schema-qualified form, etc.)

Present every issue found to the user and **wait for their response** before touching any file.

---

## Step 3 — Fix the test file

Apply the agreed corrections to the test file.

---

## Step 4 — Implement

Create `src/sqlinpython/<stmt>.py` following the patterns in existing statement modules (`vacuum.py`, `drop_table.py`, `savepoint.py`, `alter_table.py`). Export any new entry points from `src/sqlinpython/__init__.py`.

---

## Step 5 — Validate

Run `just check`. All of the following must pass before continuing:
- `ruff check` (lint)
- `ruff format --check` (formatting)
- `ty check`, `basedpyright`, `mypy` (three type checkers)
- `pytest` (all tests)

If anything fails, fix it now.

---

## Step 6 — Review coverage

Re-read the test file. Identify any cases that are missing or worth adding. Present your findings to the user and **wait for their response** before making any changes.

---

## Step 7 — Tick README

In `README.md`, change `- [ ] <stmt>-stmt` to `- [X] <stmt>-stmt`.

---

## Step 8 — Branch review

Do a pair code review with the user

---

## Step 9 — Automated Branch review

Wait for confirmation from the user before starting this step.

Spawn a **general-purpose agent** with this prompt (fill in `<stmt>` and `<branch>`):

> "You are reviewing the `feature/<stmt>-stmt` branch of the sqlinpython repository before it is squashed and merged to main. Run `git diff main..HEAD` to see all changes, then read every new or modified file in full. Produce a structured review covering: (1) correctness — does the implementation match the SQLite spec and the tests? (2) style — does it follow the patterns in the existing codebase (method ordering, `_create_query` last, `override` decorator, `from __future__ import annotations`, etc.)? (3) missing cases — any forms of the SQL statement not covered? Avoid running python scripts, if you are unaware of sqlite grammar, check the documentation. Report your findings clearly so the user can discuss them."

Present the agent's findings to the user and **stay in the conversation** so they can ask follow-up questions or request changes. Do not proceed to step 9 until the user explicitly says they are happy.

---

## Step 10 — Squash and merge

Once the user approves:

```bash
git checkout main
git merge --squash feature/<stmt>-stmt
git commit
```

Write a single commit message summarising the full feature.
