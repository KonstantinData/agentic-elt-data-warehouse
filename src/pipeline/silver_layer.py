"""
File: src/pipeline/silver_layer.py

Purpose:
  Implements the Silver layer (Step 1) of the data pipeline.  In this
  simplified implementation, the Silver layer performs basic cleaning
  and standardisation of the raw CSV files produced by the Bronze layer.
  It reads the files copied to `artifacts/runs/<run_id>/bronze/data`,
  applies type conversions and whitespace trimming, and writes the
  cleaned datasets into `artifacts/runs/<run_id>/silver/data`.

Why it exists:
  The Silver layer cleanses and standardises raw data so that
  downstream business logic and modelling can rely on consistent data
  types and formats.  Without this step, numeric fields might remain
  strings and date formats might be inconsistent, leading to
  unpredictable behaviour.

Inputs:
  - CSV files from the Bronze layer located at
    `artifacts/runs/<run_id>/bronze/data`.

Outputs:
  - Cleaned CSV files written to
    `artifacts/runs/<run_id>/silver/data`.
  - A YAML metadata file `silver_metadata.yaml` capturing column types.
  - A Markdown quality report summarising simple statistics and missing
    value counts at `artifacts/runs/<run_id>/silver/reports/silver_quality_report.md`.

Step:
  This module belongs to the Silver layer; it is part of the data
  preparation stage before feature engineering and modelling.
"""

import csv
import os
from pathlib import Path
from typing import Dict, List, Tuple
import yaml
from datetime import datetime


# NOTE: Read a CSV file and return header and rows
def _read_csv(path: Path) -> Tuple[List[str], List[List[str]]]:
    """
    Read a CSV file and return the header and list of rows.

    Args:
        path (Path): File path to read.

    Returns:
        Tuple[List[str], List[List[str]]]: (header, rows)
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [row for row in reader]
    return header, rows


# NOTE: Write a CSV file to disk
def _write_csv(path: Path, header: List[str], rows: List[List[str]]) -> None:
    """
    Write a CSV file given a header and rows.

    Args:
        path (Path): Destination file path.
        header (List[str]): Column names.
        rows (List[List[str]]): Data rows.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


# NOTE: Clean a single CSV row by trimming whitespace and coercing types
def _clean_row(header: List[str], row: List[str]) -> List[str]:
    """
    Clean a single row by trimming whitespace and normalising dates and numerics.

    Args:
        header (List[str]): Column names for the row.
        row (List[str]): Raw row values.

    Returns:
        List[str]: Cleaned row values.
    """
    cleaned = []
    for col, value in zip(header, row):
        val = value.strip()
        # NOTE: Convert numeric columns if applicable
        if col in {"quantity", "unit_price", "price"}:
            try:
                # convert to float then back to string for CSV
                val = str(float(val))
            except ValueError:
                val = ""
        # NOTE: Standardise date columns to ISO format
        elif col in {"date_of_birth", "transaction_date"}:
            try:
                dt = datetime.fromisoformat(val)
                val = dt.date().isoformat()
            except ValueError:
                val = ""
        cleaned.append(val)
    return cleaned


# NOTE: Execute the Silver layer for a given run ID
def run_silver(run_id: str) -> None:
    """
    Entry point for the Silver layer.

    Args:
        run_id (str): Unique identifier for this pipeline run.
    """
    # NOTE: Define Bronze and Silver directories
    project_root = Path(__file__).resolve().parents[2]
    bronze_data = project_root / "artifacts" / "runs" / run_id / "bronze" / "data"
    silver_data = project_root / "artifacts" / "runs" / run_id / "silver" / "data"
    silver_meta = project_root / "artifacts" / "runs" / run_id / "silver" / "_meta"
    silver_reports = project_root / "artifacts" / "runs" / run_id / "silver" / "reports"
    silver_meta.mkdir(parents=True, exist_ok=True)
    silver_reports.mkdir(parents=True, exist_ok=True)
    metadata: Dict[str, Dict[str, str]] = {}
    report_lines: List[str] = ["# Silver Layer Quality Report", "", f"Run ID: {run_id}", ""]
    # Process each CSV file
    for file_path in bronze_data.glob("*.csv"):
        header, rows = _read_csv(file_path)
        cleaned_rows = [_clean_row(header, row) for row in rows]
        # Write cleaned CSV
        out_path = silver_data / file_path.name
        _write_csv(out_path, header, cleaned_rows)
        # Record column types (simplistic: store as string, float, date)
        column_types: Dict[str, str] = {}
        for col, value in zip(header, cleaned_rows[0] if cleaned_rows else header):
            if col in {"quantity", "unit_price", "price"}:
                column_types[col] = "float"
            elif col in {"date_of_birth", "transaction_date"}:
                column_types[col] = "date"
            else:
                column_types[col] = "string"
        metadata[file_path.name] = column_types
        # Summarise missing values
        missing_counts = {col: 0 for col in header}
        for row in cleaned_rows:
            for col, val in zip(header, row):
                if val == "":
                    missing_counts[col] += 1
        report_lines.append(f"## {file_path.name}")
        for col in header:
            report_lines.append(f"- {col}: {missing_counts[col]} missing values")
        report_lines.append("")
    # Save metadata YAML
    with open(silver_meta / "silver_metadata.yaml", "w") as f:
        yaml.dump(metadata, f)
    # Save report
    (silver_reports / "silver_quality_report.md").write_text("\n".join(report_lines), encoding="utf-8")
