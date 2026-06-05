# TODO

- [ ] Implement `sql-stmt-list` and `sql-stmt` (the top-level statement wrappers from the SQLite grammar)
- [ ] Create a `functions` module exposing common SQL functions as typed helpers, so `func.avg(col("x"))` can be used instead of `FunctionName("AVG")(col("x"))`
- [ ] Investigate unifying `TableName` and `TableRef` into a single class, if their roles overlap enough to make this clean
