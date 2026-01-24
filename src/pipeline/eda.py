"""
File: src/pipeline/eda.py

Purpose:
  Implements Step 3: Exploratory Data Analysis (EDA) for the
  consolidated dataset.  The EDA summarises key descriptive
  statistics across the Gold wide sales table, including row counts,
  summary statistics of numeric fields, and counts per categorical
  values.  The results are saved into a JSON summary and a Markdown
  report for stakeholders.

Why it exists:
  Understanding the structure and distribution of the data is a
  prerequisite for effective feature engineering and modelling.

Inputs:
  - `gold_wide_sales_enriched.csv` from the Gold layer located at
    `artifacts/runs/<run_id>/gold/data`.

Outputs:
  - `eda_summary.json` containing aggregated statistics.
  - `eda_report.md` providing a human‑readable summary of the EDA.

Step:
  This module belongs to the EDA step and must be executed after the
  Gold layer and before feature engineering.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Any


# NOTE: Execute the EDA step for a given run ID
def run_eda(run_id: str) -> None:
    """
    Entry point for the EDA step.

    Args:
        run_id (str): Unique identifier for this pipeline run.
    """
    # NOTE: Locate the Gold wide table
    project_root = Path(__file__).resolve().parents[2]
    gold_data = project_root / "artifacts" / "runs" / run_id / "gold" / "data"
    eda_dir = project_root / "artifacts" / "runs" / run_id / "step1_eda"
    eda_dir.mkdir(parents=True, exist_ok=True)
    wide_path = gold_data / "gold_wide_sales_enriched.csv"
    header: List[str]
    rows: List[List[str]]
    with open(wide_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [row for row in reader]
    # Compute summary statistics
    summary: Dict[str, Any] = {
        "row_count": len(rows),
        "categorical_counts": {},
        "numeric_summary": {},
    }
    # Identify numeric columns
    numeric_cols = {"price", "quantity", "unit_price"}
    # Initialize counters
    for col in header:
        if col in numeric_cols:
            summary["numeric_summary"][col] = {
                "min": None,
                "max": None,
                "sum": 0.0,
            }
        else:
            summary["categorical_counts"][col] = {}
    # Iterate rows
    for row in rows:
        for col, value in zip(header, row):
            if col in numeric_cols:
                if value == "":
                    continue
                val = float(value)
                col_stat = summary["numeric_summary"][col]
                col_stat["sum"] += val
                col_stat["min"] = val if col_stat["min"] is None else min(col_stat["min"], val)
                col_stat["max"] = val if col_stat["max"] is None else max(col_stat["max"], val)
            else:
                cat_counts = summary["categorical_counts"][col]
                cat_counts[value] = cat_counts.get(value, 0) + 1
    # Compute averages for numeric columns
    for col, stats in summary["numeric_summary"].items():
        count = summary["row_count"]
        stats["avg"] = stats["sum"] / count if count > 0 else None
    # Write JSON summary
    summary_path = eda_dir / "data" / "eda_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    # Write Markdown report
    report_lines: List[str] = ["# EDA Report", "", f"Run ID: {run_id}", ""]
    report_lines.append(f"Total rows: {summary['row_count']}")
    report_lines.append("")
    report_lines.append("## Numeric Columns Summary")
    for col, stats in summary["numeric_summary"].items():
        report_lines.append(f"- {col}: min={stats['min']}, max={stats['max']}, avg={stats['avg']:.2f}")
    report_lines.append("")
    report_lines.append("## Categorical Value Counts (top 5)")
    for col, counts in summary["categorical_counts"].items():
        # Show only top 5 frequent values for brevity
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
        counts_str = ", ".join([f"{v}: {c}" for v, c in sorted_counts])
        report_lines.append(f"- {col}: {counts_str}")
    report_path = eda_dir / "reports" / "eda_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
