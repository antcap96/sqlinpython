from sqlinpython.alter_table import AlterTableStatement as AlterTableStatement
from sqlinpython.analyze import AnalyzeStatement as AnalyzeStatement
from sqlinpython.attach import AttachStatement as AttachStatement
from sqlinpython.create_index import CreateIndexStatement as CreateIndexStatement
from sqlinpython.create_table import CreateTableStatement as CreateTableStatement
from sqlinpython.create_view import CreateViewStatement as CreateViewStatement
from sqlinpython.create_vtable import (
    CreateVirtualTableStatement as CreateVirtualTableStatement,
)
from sqlinpython.delete import DeleteStatement as DeleteStatement
from sqlinpython.delete import DeleteStatementLimited as DeleteStatementLimited
from sqlinpython.detach import DetachStatement as DetachStatement
from sqlinpython.drop import DropIndexStatement as DropIndexStatement
from sqlinpython.drop import DropStatement as DropStatement
from sqlinpython.drop import DropTableStatement as DropTableStatement
from sqlinpython.drop import DropTriggerStatement as DropTriggerStatement
from sqlinpython.drop import DropViewStatement as DropViewStatement
from sqlinpython.insert import InsertStatement as InsertStatement
from sqlinpython.pragma import PragmaStatement as PragmaStatement
from sqlinpython.reindex import ReindexStatement as ReindexStatement
from sqlinpython.savepoint import ReleaseStatement as ReleaseStatement
from sqlinpython.savepoint import RollbackStatement as RollbackStatement
from sqlinpython.savepoint import SavepointStatement as SavepointStatement
from sqlinpython.select_base import SelectStatement as SelectStatement
from sqlinpython.transaction import BeginStatement as BeginStatement
from sqlinpython.transaction import CommitStatement as CommitStatement
from sqlinpython.update import UpdateStatement as UpdateStatement
from sqlinpython.update import UpdateStatementLimited as UpdateStatementLimited
from sqlinpython.vacuum import VacuumStatement as VacuumStatement
