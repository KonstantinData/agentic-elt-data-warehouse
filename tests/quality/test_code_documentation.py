"""
Test that all Python files under src/ conform to the documentation
standard required by the repository.  Each file must have a module
docstring describing its purpose, inputs, outputs and pipeline step.
Each public class and function must be preceded by a `# NOTE:`
comment, and longer functions must contain internal `# NOTE:` blocks.
"""

import ast
import os
from pathlib import Path


def get_python_files() -> list[Path]:
    """Return all Python files under src/ (excluding tests)."""
    root = Path("src")
    return [p for p in root.rglob("*.py") if "tests" not in p.parts]


def test_module_docstrings():
    """Every Python file must have a module docstring."""
    for path in get_python_files():
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        assert ast.get_docstring(tree), f"Missing module docstring in {path}"


def _has_preceding_note(lines: list[str], lineno: int) -> bool:
    """
    Check up to two lines above a line number for a NOTE comment.
    """
    for offset in range(1, 3):
        idx = lineno - offset - 1  # line numbers start at 1
        if idx >= 0 and lines[idx].lstrip().startswith("# NOTE:"):
            return True
    return False


def test_notes_on_classes_and_functions():
    """Check that each class and public function has a preceding NOTE."""
    for path in get_python_files():
        lines = path.read_text().splitlines()
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # skip private or dunder names
                if node.name.startswith("_"):
                    continue
                assert _has_preceding_note(lines, node.lineno), f"Missing # NOTE above {node.name} in {path}"


def test_long_functions_have_internal_notes():
    """Functions longer than 25 lines must contain at least 3 internal NOTE comments."""
    for path in get_python_files():
        lines = path.read_text().splitlines()
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                start = node.lineno - 1
                end = node.end_lineno if hasattr(node, "end_lineno") else node.lineno
                length = end - start
                if length > 25:
                    # Count internal NOTES inside function body
                    note_count = 0
                    for i in range(start, end):
                        if lines[i].lstrip().startswith("# NOTE:"):
                            note_count += 1
                    assert note_count >= 3, f"Function {node.name} in {path} lacks internal # NOTE blocks"
