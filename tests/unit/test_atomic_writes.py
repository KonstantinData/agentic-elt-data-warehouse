from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.runs import load_2_silver_layer as silver
from src.runs import load_3_gold_layer as gold


@pytest.mark.unit
@pytest.mark.parametrize(
    ("module", "atomic_to_csv", "path_factory"),
    [
        (silver, silver.atomic_to_csv, lambda p: str(p)),
        (gold, gold.atomic_to_csv, lambda p: p),
    ],
)
def test_atomic_to_csv_cleans_tmp_on_replace_failure(
    tmp_path: Path,
    module,
    atomic_to_csv,
    path_factory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    df = pd.DataFrame({"a": [1, 2]})
    target = tmp_path / "output.csv"
    tmp_path_expected = target.with_name(f".{target.name}.tmp")

    def raise_permission_error(src: str | Path, dst: str | Path) -> None:
        raise PermissionError("replace failed")

    monkeypatch.setattr(module.os, "replace", raise_permission_error)

    with pytest.raises(PermissionError):
        atomic_to_csv(df, path_factory(target), index=False)

    assert not target.exists()
    assert not tmp_path_expected.exists()
