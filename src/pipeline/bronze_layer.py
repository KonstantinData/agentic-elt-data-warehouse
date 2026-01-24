"""
File: src/pipeline/bronze_layer.py

Purpose:
  Implements the Bronze layer (Step 0) of the data pipeline.  In this
  simplified example, the Bronze layer copies raw CSV files from the
  `raw/` directory into a run‑scoped folder under
  `artifacts/runs/<run_id>/bronze/data` without any transformation.

Why it exists:
  The Bronze layer preserves raw snapshots of the input CRM and ERP
  systems.  Keeping an immutable copy of the raw data is critical for
  auditability and reproducibility.  Downstream cleaning and analysis
  steps always refer back to these snapshots to ensure a consistent
  foundation.

Inputs:
  - Raw CSV files located under `raw/source_crm/` and `raw/source_erp/`.

Outputs:
  - Copies of these files written into
    `artifacts/runs/<run_id>/bronze/data/`.
  - A simple Markdown report written to
    `artifacts/runs/<run_id>/bronze/reports/bronze_report.md` summarising
    the number of rows in each file.
  - A metadata YAML file written to
    `artifacts/runs/<run_id>/bronze/_meta/bronze_metadata.yaml` listing
    file checksums and timestamps.

Step:
  EDA / Feature Engineering / Segmentation & Clustering / Reporting:
  This module belongs to the Bronze layer and prepares data for
  subsequent steps.
"""

import csv
import hashlib
import os
from pathlib import Path
from typing import Dict, List


# NOTE: Compute the SHA256 checksum for a given file
def _sha256_file(path: Path) -> str:
    """
    Compute the SHA256 checksum of a file's contents.

    Args:
        path (Path): Path to the file.

    Returns:
        str: Hexadecimal SHA256 checksum.
    """
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


# NOTE: Copy raw CSV files into the Bronze directory and record checksums
def _copy_raw_to_bronze(raw_dir: Path, bronze_data_dir: Path) -> Dict[str, Dict[str, str]]:
    """
    Copy all CSV files from a raw directory into the Bronze data directory.

    For each file copied, record its checksum and modification time.

    Args:
        raw_dir (Path): Directory containing raw CSV files.
        bronze_data_dir (Path): Destination directory within the run folder.

    Returns:
        Dict[str, Dict[str, str]]: Mapping from filename to checksum and mtime.
    """
    # NOTE: Ensure destination exists before copying files
    bronze_data_dir.mkdir(parents=True, exist_ok=True)
    metadata: Dict[str, Dict[str, str]] = {}
    for file_path in raw_dir.glob("*.csv"):
        dest_path = bronze_data_dir / file_path.name
        dest_path.write_bytes(file_path.read_bytes())
        metadata[file_path.name] = {
            "checksum": _sha256_file(dest_path),
            "mtime": str(file_path.stat().st_mtime),
        }
    return metadata


# NOTE: Execute the Bronze layer for a given run ID
def run_bronze(run_id: str) -> None:
    """
    Entry point for the Bronze layer.

    This function copies all raw input files into the run‑scoped Bronze
    folder, computes checksums, and writes a simple report and metadata.

    Args:
        run_id (str): Unique identifier for this pipeline run.
    """
    # NOTE: Define paths for raw data and Bronze outputs
    project_root = Path(__file__).resolve().parents[2]
    raw_crm = project_root / "raw" / "source_crm"
    raw_erp = project_root / "raw" / "source_erp"
    run_root = project_root / "artifacts" / "runs" / run_id
    bronze_data = run_root / "bronze" / "data"
    bronze_meta = run_root / "bronze" / "_meta"
    bronze_reports = run_root / "bronze" / "reports"
    # Copy CRM and ERP files
    crm_meta = _copy_raw_to_bronze(raw_crm, bronze_data)
    erp_meta = _copy_raw_to_bronze(raw_erp, bronze_data)
    # Merge metadata and ensure meta directory exists
    bronze_meta.mkdir(parents=True, exist_ok=True)
    bronze_reports.mkdir(parents=True, exist_ok=True)
    # Write metadata YAML
    import yaml  # local import to avoid top-level dependency if not used

    meta_contents = {"crm": crm_meta, "erp": erp_meta}
    with open(bronze_meta / "bronze_metadata.yaml", "w") as f:
        yaml.dump(meta_contents, f)
    # Create a simple report summarising row counts
    report_lines: List[str] = ["# Bronze Layer Report", "", f"Run ID: {run_id}", ""]
    for file_name in sorted(meta_contents.get("crm", {}).keys() | meta_contents.get("erp", {}).keys()):
        file_path = bronze_data / file_name
        try:
            with open(file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                row_count = sum(1 for _ in reader) - 1  # subtract header
        except FileNotFoundError:
            row_count = 0
        report_lines.append(f"- {file_name}: {row_count} rows")
    report_path = bronze_reports / "bronze_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    # NOTE: Bronze layer completed; nothing is returned as it writes files to disk
