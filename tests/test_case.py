from sqlinpython import Case, ColumnRef, Value


def test_case_1() -> None:
    assert (
        Case(ColumnRef("CNT"))
        .When(Value(0))
        .Then(Value("No"))
        .When(Value(1))
        .Then(Value("One"))
        .Else(Value("Some"))
        .End._create_query()
        == "CASE CNT WHEN 0 THEN 'No' WHEN 1 THEN 'One' ELSE 'Some' END"
    )


def test_case_2() -> None:
    assert (
        Case.When(ColumnRef("CNT") < Value(10))
        .Then(Value("Low"))
        .Else(Value("High"))
        .End._create_query()
        == "CASE WHEN CNT < 10 THEN 'Low' ELSE 'High' END"
    )
