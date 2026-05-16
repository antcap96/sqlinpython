from sqlinpython import Release, Rollback, Savepoint


def test_savepoint_basic() -> None:
    assert Savepoint("a").get_query() == "SAVEPOINT a"


def test_savepoint_quoted_name() -> None:
    assert Savepoint('a"').get_query() == 'SAVEPOINT "a"""'


def test_release_basic() -> None:
    assert Release("a").get_query() == "RELEASE a"


def test_release_savepoint() -> None:
    assert Release.Savepoint("a").get_query() == "RELEASE SAVEPOINT a"


def test_release_savepoint_quoted_name() -> None:
    assert Release.Savepoint('a"').get_query() == 'RELEASE SAVEPOINT "a"""'


def test_rollback_no_args() -> None:
    assert Rollback.get_query() == "ROLLBACK"


def test_rollback_to() -> None:
    assert Rollback.To("a").get_query() == "ROLLBACK TO a"


def test_rollback_to_quoted_name() -> None:
    assert Rollback.To('a"').get_query() == 'ROLLBACK TO "a"""'


def test_rollback_to_savepoint() -> None:
    assert Rollback.To.Savepoint("a").get_query() == "ROLLBACK TO SAVEPOINT a"


def test_rollback_transaction_to() -> None:
    assert Rollback.Transaction.To("a").get_query() == "ROLLBACK TRANSACTION TO a"


def test_rollback_transaction_to_savepoint() -> None:
    assert (
        Rollback.Transaction.To.Savepoint("a").get_query()
        == "ROLLBACK TRANSACTION TO SAVEPOINT a"
    )


def test_rollback_transaction_to_savepoint_quoted_name() -> None:
    assert (
        Rollback.Transaction.To.Savepoint('a"').get_query()
        == 'ROLLBACK TRANSACTION TO SAVEPOINT "a"""'
    )
