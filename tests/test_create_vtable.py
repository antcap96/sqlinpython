from sqlinpython import Create


def test_create_virtual_table() -> None:
    assert (
        Create.VirtualTable("my_vtable").Using("fts5").get_query()
        == "CREATE VIRTUAL TABLE my_vtable USING fts5"
    )
    assert (
        Create.VirtualTable.IfNotExists("my_vtable").Using("fts5").get_query()
        == "CREATE VIRTUAL TABLE IF NOT EXISTS my_vtable USING fts5"
    )
    assert (
        Create.VirtualTable("main", "my_vtable").Using("fts5").get_query()
        == "CREATE VIRTUAL TABLE main.my_vtable USING fts5"
    )
    assert (
        Create.VirtualTable.IfNotExists("main", "my_vtable").Using("fts5").get_query()
        == "CREATE VIRTUAL TABLE IF NOT EXISTS main.my_vtable USING fts5"
    )
    assert (
        Create.VirtualTable("my_vtable").Using("fts5")("content").get_query()
        == "CREATE VIRTUAL TABLE my_vtable USING fts5(content)"
    )
    assert (
        Create.VirtualTable("my_vtable").Using("fts5")("content", "title").get_query()
        == "CREATE VIRTUAL TABLE my_vtable USING fts5(content, title)"
    )
    assert (
        Create.VirtualTable("my_vtable")
        .Using("fts5")("content", "tokenize = 'porter'")
        .get_query()
        == "CREATE VIRTUAL TABLE my_vtable USING fts5(content, tokenize = 'porter')"
    )
    assert (
        Create.VirtualTable.IfNotExists("main", "my_vtable")
        .Using("fts5")("content")
        .get_query()
        == "CREATE VIRTUAL TABLE IF NOT EXISTS main.my_vtable USING fts5(content)"
    )
