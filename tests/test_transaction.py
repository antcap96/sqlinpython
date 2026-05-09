from sqlinpython import Begin, Commit, End


def test_begin() -> None:
    assert Begin.get_query() == "BEGIN"


def test_begin_deferred() -> None:
    assert Begin.Deferred.get_query() == "BEGIN DEFERRED"


def test_begin_immediate() -> None:
    assert Begin.Immediate.get_query() == "BEGIN IMMEDIATE"


def test_begin_exclusive() -> None:
    assert Begin.Exclusive.get_query() == "BEGIN EXCLUSIVE"


def test_begin_transaction() -> None:
    assert Begin.Transaction.get_query() == "BEGIN TRANSACTION"


def test_begin_deferred_transaction() -> None:
    assert Begin.Deferred.Transaction.get_query() == "BEGIN DEFERRED TRANSACTION"


def test_begin_immediate_transaction() -> None:
    assert Begin.Immediate.Transaction.get_query() == "BEGIN IMMEDIATE TRANSACTION"


def test_begin_exclusive_transaction() -> None:
    assert Begin.Exclusive.Transaction.get_query() == "BEGIN EXCLUSIVE TRANSACTION"


def test_commit() -> None:
    assert Commit.get_query() == "COMMIT"


def test_commit_transaction() -> None:
    assert Commit.Transaction.get_query() == "COMMIT TRANSACTION"


def test_end() -> None:
    assert End.get_query() == "END"


def test_end_transaction() -> None:
    assert End.Transaction.get_query() == "END TRANSACTION"
