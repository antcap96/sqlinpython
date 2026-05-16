from sqlinpython import Create


def test_create_virtual_table_basic() -> None:
    assert (
        Create.VirtualTable("my_vtable").Using("fts5").get_query()
        == "CREATE VIRTUAL TABLE my_vtable USING fts5"
    )


def test_create_virtual_table_if_not_exists() -> None:
    assert (
        Create.VirtualTable.IfNotExists("my_vtable").Using("fts5").get_query()
        == "CREATE VIRTUAL TABLE IF NOT EXISTS my_vtable USING fts5"
    )


def test_create_virtual_table_schema_qualified() -> None:
    assert (
        Create.VirtualTable("main", "my_vtable").Using("fts5").get_query()
        == "CREATE VIRTUAL TABLE main.my_vtable USING fts5"
    )


def test_create_virtual_table_if_not_exists_schema_qualified() -> None:
    assert (
        Create.VirtualTable.IfNotExists("main", "my_vtable").Using("fts5").get_query()
        == "CREATE VIRTUAL TABLE IF NOT EXISTS main.my_vtable USING fts5"
    )


def test_create_virtual_table_single_module_arg() -> None:
    assert (
        Create.VirtualTable("my_vtable").Using("fts5")("content").get_query()
        == "CREATE VIRTUAL TABLE my_vtable USING fts5(content)"
    )


def test_create_virtual_table_multiple_module_args() -> None:
    assert (
        Create.VirtualTable("my_vtable").Using("fts5")("content", "title").get_query()
        == "CREATE VIRTUAL TABLE my_vtable USING fts5(content, title)"
    )


def test_create_virtual_table_module_arg_with_option() -> None:
    assert (
        Create.VirtualTable("my_vtable")
        .Using("fts5")("content", "tokenize = 'porter'")
        .get_query()
        == "CREATE VIRTUAL TABLE my_vtable USING fts5(content, tokenize = 'porter')"
    )


def test_create_virtual_table_if_not_exists_schema_qualified_with_module_arg() -> None:
    assert (
        Create.VirtualTable.IfNotExists("main", "my_vtable")
        .Using("fts5")("content")
        .get_query()
        == "CREATE VIRTUAL TABLE IF NOT EXISTS main.my_vtable USING fts5(content)"
    )
