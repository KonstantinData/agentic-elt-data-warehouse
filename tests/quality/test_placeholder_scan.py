"""
Scan markdown and notebook files for forbidden placeholder tokens.

This test ensures that documentation and notebook files do not
contain unaddressed placeholders such as TODO, TBD, placeholder,
later or ellipsis (...).  If any token is found the test fails.
"""

import json
from pathlib import Path

FORBIDDEN = {"TODO", "TBD", "placeholder", "tbd", "later", "..."}


def get_text_files() -> list[Path]:
    """Gather all markdown files and notebook files in the repository."""
    files = []
    for pattern in ["*.md", "*.ipynb"]:
        files.extend(Path(".").rglob(pattern))
    # Exclude virtual environment or artifacts
    return [f for f in files if not f.parts[0].startswith("artifacts") and not f.parts[0].startswith(".git")]


def test_no_placeholders():
    """Assert that no forbidden tokens appear in docs or notebooks."""
    for path in get_text_files():
        if path.suffix == ".ipynb":
            # Parse notebook JSON
            try:
                data = json.loads(path.read_text())
            except json.JSONDecodeError:
                continue
            # Check each cell's source lines
            for cell in data.get("cells", []):
                source = "".join(cell.get("source", []))
                for token in FORBIDDEN:
                    assert token not in source, f"Forbidden token '{token}' found in {path}"
        else:
            content = path.read_text(encoding="utf-8")
            for token in FORBIDDEN:
                assert token not in content, f"Forbidden token '{token}' found in {path}"
