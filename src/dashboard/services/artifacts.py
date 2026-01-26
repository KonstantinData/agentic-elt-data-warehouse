from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Literal

import pandas as pd
import yaml

LayoutType = Literal["canonical", "legacy"]


@dataclass(frozen=True)
class RunLocation:
    run_id: str
    data_dir: Path
    metadata_path: Path
    layout: LayoutType

    @property
    def artifact_label(self) -> str:
        return (
            f"artifacts/runs/{self.run_id}/silver/data"
            if self.layout == "canonical"
            else f"artifacts/silver/{self.run_id}/data"
        )


def find_repo_root() -> Path:
    """Walk upward until we find a repo containing `src/` and `artifacts/`."""
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / "src").exists() and (current / "artifacts").exists():
            return current
        current = current.parent
    return current


def _collect_runs(root: Path, layout: LayoutType) -> Iterable[RunLocation]:
    """Collect run descriptors for either canonical or legacy layout."""
    if layout == "canonical":
        base_path = root / "artifacts" / "runs"
        silver_suffix = Path("silver") / "data"
    else:
        base_path = root / "artifacts" / "silver"
        silver_suffix = Path("data")

    if not base_path.exists():
        return []

    runs = []
    for run_dir in base_path.iterdir():
        if not run_dir.is_dir():
            continue
        data_dir = run_dir / silver_suffix
        metadata_path = data_dir / "metadata.yaml"
        if not data_dir.exists():
            continue
        runs.append(
            RunLocation(
                run_id=run_dir.name,
                    data_dir=data_dir,
                    metadata_path=metadata_path,
                    layout=layout,
                )
            )
    return runs


def list_available_runs() -> list[RunLocation]:
    """Return available runs, preferring canonical layout and keeping sorted order."""
    repo_root = find_repo_root()
    canonical = {run.run_id: run for run in _collect_runs(repo_root, "canonical")}
    if canonical:
        entries = sorted(canonical.values(), key=lambda run: run.run_id, reverse=True)
        return entries

    legacy = {run.run_id: run for run in _collect_runs(repo_root, "legacy")}
    return sorted(legacy.values(), key=lambda run: run.run_id, reverse=True)


def explain_missing_artifacts() -> str:
    """Guide users when artifact discovery returns nothing."""
    return (
        "No Silver artifacts were detected. Run the ELT pipeline first:\n"
        "  python .\\src\\runs\\start_run.py  (Windows)\n"
        "  python ./src/runs/start_run.py    (Linux/macOS)\n"
        "Expected layout:\n"
        "  artifacts/runs/<run_id>/silver/data/  (preferred)\n"
        "  artifacts/silver/<run_id>/data/       (legacy fallback)\n"
    )


@lru_cache(maxsize=64)
def _load_yaml(path: Path) -> dict | None:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as source:
        return yaml.safe_load(source) or {}


@lru_cache(maxsize=64)
def _load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def load_run_metadata(run_location: RunLocation) -> dict:
    """Load metadata for a given run, or return an empty dict if missing."""
    return _load_yaml(run_location.metadata_path)


REQUIRED_TABLES = {
    "sales": "sales_details.csv",
    "product": "prd_info.csv",
    "customer": "cst_info.csv",
    "location": "LOC_A101.csv",
}


def load_required_tables(run_location: RunLocation) -> dict[str, pd.DataFrame] | None:
    """Load all tables required by the dashboard; return None if any table is missing."""
    tables = {}
    for name, filename in REQUIRED_TABLES.items():
        path = run_location.data_dir / filename
        if not path.exists():
            return None
        tables[name] = _load_csv(path)
    return tables


def explain_layout(run_location: RunLocation | None) -> str:
    if run_location is None:
        return "No run selected."
    return (
        "canonical artifact contract"
        if run_location.layout == "canonical"
        else "legacy artifact layout"
    )
