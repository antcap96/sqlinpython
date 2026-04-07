# Auto-detect nix shell: skip prefix when already inside
run := if env_var_or_default("IN_NIX_SHELL", "") != "" { "" } else { "nix develop --command " }

# Run all tests
test:
    {{run}}pytest

# Run a specific test file or function: just test-one tests/test_select.py::test_join
test-one TEST:
    {{run}}pytest {{TEST}}

# Type checkers
ty:
    {{run}}ty check

pyright:
    {{run}}basedpyright

mypy:
    {{run}}mypy .

types: ty pyright mypy

# Linting / formatting
lint:
    {{run}}ruff check

fmt:
    {{run}}ruff format

fix:
    {{run}}ruff check --fix
    {{run}}ruff format

# Full CI-equivalent check
check: lint types test
