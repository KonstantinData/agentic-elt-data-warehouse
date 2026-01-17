from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.utils import atomic_io


@pytest.mark.unit
def test_atomic_write_text_cleans_tmp_on_replace_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "notes.txt"
    tmp_path_expected = target.with_name(f".{target.name}.tmp")

    def raise_permission_error(src: str | Path, dst: str | Path) -> None:
        raise PermissionError("replace failed")

    monkeypatch.setattr(atomic_io.os, "replace", raise_permission_error)

    with pytest.raises(PermissionError):
        atomic_io.atomic_write_text("hello", target)

    assert not target.exists()
    assert not tmp_path_expected.exists()


@pytest.mark.unit
def test_atomic_to_csv_cleans_tmp_on_replace_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    df = pd.DataFrame({"a": [1, 2]})
    target = tmp_path / "output.csv"
    tmp_path_expected = target.with_name(f".{target.name}.tmp")

    def raise_permission_error(src: str | Path, dst: str | Path) -> None:
        raise PermissionError("replace failed")

    monkeypatch.setattr(atomic_io.os, "replace", raise_permission_error)

    with pytest.raises(PermissionError):
        atomic_io.atomic_to_csv(df, target, index=False)

    assert not target.exists()
    assert not tmp_path_expected.exists()
