# sqlinpython

This is a small toy library to integrate SQL into a python project. The library allows to write python code that is very similar to a SQL query that then can be converted to the query string with the get_query method. The advantage this brings over having the raw strings in the code is editor auto-complete and static syntax check, since the library is fully type annotated.

The type checks are only made with external tools like [mypy](https://github.com/python/mypy) and are not made at runtime.

## Examples

A simple example usage of this library might look like this:

```python
from sqlinpython import Select, TableRef, col
assert (
    Select(col("a")).From(TableRef("b")).get_query()
    == "SELECT a FROM b"
)
```

But the library is capable of much more complex queries like the following:

```python
from sqlinpython import Select, TableRef, FunctionName, col, literal
assert (
    Select(col("full_name"))
    .From(TableRef("SALES_PERSON"))
    .Where(col("ranking") >= literal(5.0))
    .UnionAll(
        Select(col("reviewer_name"))
        .From(TableRef("CUSTOMER_REVIEW"))
        .GroupBy(col("reviewer_name"))
        .Having(FunctionName("AVG")(col("score")) >= literal(8.0))
    )
    .get_query()
    == "SELECT full_name FROM SALES_PERSON WHERE ranking >= 5.0 UNION ALL SELECT reviewer_name FROM CUSTOMER_REVIEW GROUP BY reviewer_name HAVING AVG(score) >= 8.0"
)
```

Although for larger queries, for the sake of readability, you should probably split up the components into variables:

```python
sales_people = (
    Select(col("full_name"))
    .From(TableRef("SALES_PERSON"))
    .Where(col("ranking") >= literal(5.0))
)
reviewers = (
    Select(col("reviewer_name"))
    .From(TableRef("CUSTOMER_REVIEW"))
    .GroupBy(col("reviewer_name"))
    .Having(FunctionName("AVG")(col("score")) >= literal(8.0))
)
assert (
    sales_people.UnionAll(reviewers).get_query()
    == "SELECT full_name FROM SALES_PERSON WHERE ranking >= 5.0 UNION ALL SELECT reviewer_name FROM CUSTOMER_REVIEW GROUP BY reviewer_name HAVING AVG(score) >= 8.0"
)
```

Further examples can be seen in the [tests](./tests) directory.

## Potential problems

In order to only allow valid SQL syntax, the library creates hundreds of different types. A naming convention is adhered to try to make these types somewhat manageable, but it isn't always obvious what the type should be if you decide to create a function that outputs an incomplete sql query.
For example, a select query of the type ``Select(...).From(...)`` has the type ``SelectStatementWithFrom``, while the type of a select query of the type ``Select(...)`` has the type ``SelectStatementWithSelectExpression``.

These types are not yet part of a public api and their names might be changed in the future.
