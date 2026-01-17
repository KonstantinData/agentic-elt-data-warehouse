from __future__ import annotations

from pathlib import Path
import re

import pytest


@pytest.mark.unit
def test_no_disallowed_io_patterns_in_selected_files() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    template_dir = repo_root / "src" / "templates"
    template_paths = sorted(template_dir.glob("*.py"))

    target_files = [
        repo_root / "src" / "runs" / "load_1_bronze_layer.py",
        repo_root / "src" / "runs" / "load_summary_report.py",
        *template_paths,
    ]

    pattern_map = {
        ".to_csv(": re.compile(r"\\.to_csv\\("),
        "Path.write_text(": re.compile(r"Path\\.write_text\\("),
        "open(...,\"w\")": re.compile(r"open\\([^\\n]*,\\s*['\\\"]w['\\\"]"),
    }

    for path in target_files:
        contents = path.read_text(encoding="utf-8")
        for label, pattern in pattern_map.items():
            assert not pattern.search(contents), f"Found disallowed pattern {label} in {path}"
