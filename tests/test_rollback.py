from sqlinpython import Release, Rollback, Savepoint


def test_savepoint() -> None:
    assert Savepoint("a").get_query() == "SAVEPOINT a"
    assert Savepoint('a"').get_query() == 'SAVEPOINT "a"""'


def test_release() -> None:
    assert Release("a").get_query() == "RELEASE a"
    assert Release.Savepoint("a").get_query() == "RELEASE SAVEPOINT a"
    assert Release.Savepoint('a"').get_query() == 'RELEASE SAVEPOINT "a"""'


def test_rollback() -> None:
    assert Rollback.get_query() == "ROLLBACK"
    assert Rollback.To("a").get_query() == "ROLLBACK TO a"
    assert Rollback.To('a"').get_query() == 'ROLLBACK TO "a"""'
    assert Rollback.To.Savepoint("a").get_query() == "ROLLBACK TO SAVEPOINT a"
    assert Rollback.Transaction.To("a").get_query() == "ROLLBACK TRANSACTION TO a"
    assert (
        Rollback.Transaction.To.Savepoint("a").get_query()
        == "ROLLBACK TRANSACTION TO SAVEPOINT a"
    )
    assert (
        Rollback.Transaction.To.Savepoint('a"').get_query()
        == 'ROLLBACK TRANSACTION TO SAVEPOINT "a"""'
    )
