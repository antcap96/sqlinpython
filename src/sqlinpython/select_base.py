from __future__ import annotations

from abc import ABC

from sqlinpython.base import CompleteSqlQuery

# Type tags used to track which SELECT statements may appear as compound operands
# (UNION / INTERSECT / EXCEPT).
#
# The rule: only a "core" select — one without ORDER BY or LIMIT — is valid on
# the right-hand side of a compound operator.  We encode this as a type
# parameter T on SelectStatement_.
#
# The trick: Core extends Complete so that SelectStatement_[Core] is accepted
# wherever SelectStatement_[Complete] is expected (e.g. as a subquery in FROM),
# but not the other way around.  Compound methods (Union, Intersect, …) accept
# only SelectStatement_[Core] as their rhs argument, so passing a statement
# that already has ORDER BY or LIMIT (which returns SelectStatement_[Complete])
# is a type error.


class Complete:
    """Marker for a fully-formed SELECT that may carry ORDER BY / LIMIT."""


class Core(Complete):
    """Marker for a SELECT without ORDER BY / LIMIT; valid as a compound operand.

    Inherits Complete so a SelectStatement_[Core] is usable anywhere a
    SelectStatement_[Complete] is expected, but not vice-versa.
    """


class SelectStatement_[T: Core | Complete](CompleteSqlQuery, ABC):
    """Abstract base for SELECT statements. Isolated to avoid circular imports."""


SelectStatement = SelectStatement_[Complete]
