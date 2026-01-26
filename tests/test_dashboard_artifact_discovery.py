from __future__ import annotations

from pathlib import Path

from src.dashboard.services import artifacts


def _create_repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    return root


def test_no_artifacts_returns_empty(monkeypatch, tmp_path):
    """No artifact directories should produce an empty run list and guidance text."""
    root = _create_repo_root(tmp_path)
    monkeypatch.setattr(artifacts, "find_repo_root", lambda: root)
    assert artifacts.list_available_runs() == []
    assert "start_run.py" in artifacts.explain_missing_artifacts()


def test_canonical_layout_detected(monkeypatch, tmp_path):
    root = _create_repo_root(tmp_path)
    run_id = "20260125_210000_#abc123"
    data_dir = root / "artifacts" / "runs" / run_id / "silver" / "data"
    data_dir.mkdir(parents=True)
    monkeypatch.setattr(artifacts, "find_repo_root", lambda: root)
    runs = artifacts.list_available_runs()
    assert runs
    assert runs[0].run_id == run_id
    assert runs[0].layout == "canonical"


def test_legacy_layout_fallback(monkeypatch, tmp_path):
    root = _create_repo_root(tmp_path)
    run_id = "legacy_20260125_210000"
    data_dir = root / "artifacts" / "silver" / run_id / "data"
    data_dir.mkdir(parents=True)
    monkeypatch.setattr(artifacts, "find_repo_root", lambda: root)
    runs = artifacts.list_available_runs()
    assert runs
    assert runs[0].run_id == run_id
    assert runs[0].layout == "legacy"
