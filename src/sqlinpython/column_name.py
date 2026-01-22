from sqlinpython.column_definition import ColumnNameWithType, WithCollate
from sqlinpython.indexed_column import IndexedColumnWithCollate
from sqlinpython.name import Name
from sqlinpython.type_name import CompleteTypeName


# Both indexed-column (https://sqlite.org/syntax/indexed-column.html) and
# column-def (https://sqlite.org/syntax/column-def.html + https://sqlite.org/syntax/column-constraint.html)
# allow ColumnName.Collate
class ColumnNameWithCollate(IndexedColumnWithCollate, WithCollate):
    pass


# TODO: Any better way to handle mypy error "incompatible with definition in base class"
class ColumnName(Name, ColumnNameWithType, IndexedColumnWithCollate):  # type: ignore [misc]
    def __call__(self, type_name: CompleteTypeName) -> ColumnNameWithType:
        return ColumnNameWithType(self, type_name)

    def Collate(self, collation_name: str | Name) -> ColumnNameWithCollate:
        if isinstance(collation_name, str):
            collation_name = Name(collation_name)
        return ColumnNameWithCollate(self, collation_name)
