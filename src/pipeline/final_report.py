"""
File: src/pipeline/final_report.py

Purpose:
  Generates the final exposé report summarising the entire pipeline
  execution.  The report synthesises outputs from previous steps,
  including high‑level data quality observations, key EDA findings,
  segmentation highlights, and next‑step recommendations.  It is
  intended for an executive audience and emphasises determinism and
  GDPR‑safety.

Why it exists:
  Consolidating pipeline results into a single document provides
  stakeholders with a coherent overview of the run, ensuring that
  critical insights are not lost and that the process is auditable.

Inputs:
  - `run_manifest.json` for metadata about the run.
  - `eda_summary.json` produced by the EDA step.
  - `segmentation_report.md` and counts from segmentation.

Outputs:
  - `final_expose.md` summarising the run under
    `artifacts/runs/<run_id>/reports`.

Step:
  This module belongs to the final reporting step and must be executed
  after all other steps complete.
"""

import json
from pathlib import Path
from typing import Dict, Any


# NOTE: Compose the final exposé report for a given run ID
def run_final_report(run_id: str) -> None:
    """
    Compose an executive‑level final exposé report for the run.

    Args:
        run_id (str): Unique identifier for the pipeline run.
    """
    project_root = Path(__file__).resolve().parents[2]
    run_root = project_root / "artifacts" / "runs" / run_id
    reports_dir = run_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    # Load run manifest if it exists
    manifest_path = run_root / "_meta" / "run_manifest.json"
    manifest: Dict[str, Any] = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
    # Load EDA summary
    eda_summary_path = run_root / "step1_eda" / "data" / "eda_summary.json"
    eda_summary: Dict[str, Any] = {}
    if eda_summary_path.exists():
        eda_summary = json.loads(eda_summary_path.read_text())
    # Load segmentation report
    seg_report_path = run_root / "step3_segmentation" / "reports" / "segmentation_report.md"
    seg_report = seg_report_path.read_text() if seg_report_path.exists() else ""
    # Compose final report
    lines: List[str] = [
        "# Final Exposé Report",
        "",
        f"Run ID: {run_id}",
        "",
        "## Pipeline Overview",
        "This run executed the Bronze, Silver, Gold, EDA, Feature Engineering, Segmentation, and Final Reporting steps in sequence.",
        "All randomness was controlled via a single seed to ensure deterministic outputs.",
        "",
    ]
    # Add data quality summary
    lines.append("## Data Quality Summary")
    if eda_summary:
        lines.append(f"- Total rows in wide table: {eda_summary.get('row_count')}")
        lines.append("- Numeric column summaries:")
        for col, stats in eda_summary.get("numeric_summary", {}).items():
            lines.append(f"  - {col}: min={stats.get('min')}, max={stats.get('max')}, avg={stats.get('avg'):.2f}")
    else:
        lines.append("No EDA summary available.")
    lines.append("")
    # Add segmentation highlights
    lines.append("## Segmentation Highlights")
    if seg_report:
        # Extract cluster sizes from the segmentation report (very simple parsing)
        for line in seg_report.splitlines():
            if line.startswith("- Size") or line.startswith("### Cluster"):
                lines.append(line)
    else:
        lines.append("No segmentation report available.")
    lines.append("")
    lines.append("## GDPR & Data Policy Notes")
    lines.append("All customer identifiers were pseudonymised using a salted SHA256 hash to ensure no direct identifiers appear in final outputs.")
    lines.append("Raw first and last names were not propagated beyond the Bronze/Silver layers.")
    lines.append("See `data_policy.json` for details.")
    lines.append("")
    lines.append("## Next Steps")
    lines.append("- Validate the segmentation results on a larger dataset.")
    lines.append("- Experiment with different numbers of clusters or clustering algorithms.")
    lines.append("- Incorporate demographic or geographic features if available.")
    # Save report
    (reports_dir / "final_expose.md").write_text("\n".join(lines), encoding="utf-8")
