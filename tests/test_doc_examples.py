import re
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).parent.parent
_DOC_FILES = [_REPO_ROOT / "README.md", *sorted((_REPO_ROOT / "docs").glob("*.md"))]

_FENCED_PYTHON_BLOCK = re.compile(
    r"^```python([^\n]*)\n(.*?)^```$", re.MULTILINE | re.DOTALL
)


def extract_blocks(doc: Path) -> list[str]:
    """Return the runnable ```python blocks of a Markdown file, in order.

    Blocks tagged ```python notest are illustrative only and excluded.
    """
    blocks: list[str] = []
    for match in _FENCED_PYTHON_BLOCK.finditer(doc.read_text()):
        info, code = match.groups()
        if "notest" not in info:
            blocks.append(code)
    return blocks


@pytest.mark.parametrize(
    "doc", _DOC_FILES, ids=[str(f.relative_to(_REPO_ROOT)) for f in _DOC_FILES]
)
def test_doc_examples(doc: Path) -> None:
    blocks = extract_blocks(doc)
    assert blocks, f"no python examples found in {doc.name}"
    namespace: dict[str, object] = {}
    for index, block in enumerate(blocks, start=1):
        code = compile(block, f"{doc.name} (block {index})", "exec")
        exec(code, namespace)
