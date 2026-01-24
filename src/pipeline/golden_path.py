"""
File: src/pipeline/golden_path.py

Purpose:
  Provides the single entry point for executing the entire data
  pipeline end‑to‑end.  This script orchestrates the Bronze, Silver,
  Gold, EDA, Feature Engineering, Segmentation, and Final Report
  steps, enforcing a deterministic seed and writing run metadata and
  data policy documents.  It unifies all outputs under the
  `artifacts/runs/<run_id>` directory.

Why it exists:
  A single orchestrator simplifies running the pipeline and ensures
  that all steps are executed in the correct order with the same run
  identifier and seed.  This fosters reproducibility and auditability.

Usage:
  This module can be executed as a CLI script.  For example:

      python -m src.pipeline.golden_path --run-id <run_id> --seed 42

  If no run ID is provided, a new one will be generated based on the
  current timestamp.

Step:
  This module coordinates all pipeline steps.  It does not belong to
  a single step but spans the entire workflow.
"""

import argparse
import json
import os
import random
import string
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from .bronze_layer import run_bronze
from .silver_layer import run_silver
from .gold_layer import run_gold
from .eda import run_eda
from .feature_engineering import run_feature_engineering
from .segmentation import run_segmentation
from .final_report import run_final_report


# NOTE: Generate a new timestamp‑based run identifier with random suffix
def _generate_run_id() -> str:
    """
    Generate a deterministic run identifier based on the current UTC
    timestamp and a random suffix.  The format is
    YYYYMMDDTHHMMSSZ_<suffix> where suffix is 4 random uppercase letters.
    """
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    suffix = "".join(random.choices(string.ascii_uppercase, k=4))
    return f"{timestamp}_{suffix}"


# NOTE: Collect raw input file paths and compute checksums
def _collect_raw_files(run_id: str) -> Dict[str, Dict[str, str]]:
    """
    Gather raw input file information (paths and checksums).

    Args:
        run_id (str): Run identifier (unused here but reserved for future).

    Returns:
        Dict[str, Dict[str, str]]: Mapping from relative path to checksum.
    """
    project_root = Path(__file__).resolve().parents[2]
    raw_dir = project_root / "raw"
    file_info: Dict[str, Dict[str, str]] = {}
    from .bronze_layer import _sha256_file
    for csv_path in raw_dir.rglob("*.csv"):
        rel = str(csv_path.relative_to(project_root))
        file_info[rel] = {
            "checksum": _sha256_file(csv_path),
        }
    return file_info


# NOTE: Write the run manifest summarising input files, seed, and step status
def _write_run_manifest(run_id: str, seed: int, status: Dict[str, str]) -> None:
    """
    Write the run manifest JSON capturing input files, seed and step status.

    Args:
        run_id (str): Run identifier.
        seed (int): Seed used for deterministic operations.
        status (Dict[str, str]): Status per pipeline step (e.g., "success", "failure").
    """
    project_root = Path(__file__).resolve().parents[2]
    run_root = project_root / "artifacts" / "runs" / run_id
    meta_dir = run_root / "_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": run_id,
        "seed": seed,
        "input_files": _collect_raw_files(run_id),
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "step_status": status,
        "repo_version": "unknown",
    }
    with open(meta_dir / "run_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


# NOTE: Write the data policy describing how personal data was handled
def _write_data_policy(run_id: str) -> None:
    """
    Write the data policy JSON summarising personal data handling.
    """
    project_root = Path(__file__).resolve().parents[2]
    run_root = project_root / "artifacts" / "runs" / run_id
    meta_dir = run_root / "_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    policy = {
        "personal_data_columns": ["firstname", "lastname"],
        "actions": {
            "firstname": "dropped",  # removed after Silver layer
            "lastname": "dropped",
            "customer_id": "pseudonymised via salted SHA256 hash",
        },
        "confirmation": "Final outputs contain no direct identifiers.",
    }
    with open(meta_dir / "data_policy.json", "w", encoding="utf-8") as f:
        json.dump(policy, f, indent=2)


# NOTE: Run the entire pipeline end‑to‑end for a given run ID and seed
def run_pipeline(run_id: str = None, seed: int = 42) -> None:
    """
    Execute the full pipeline end‑to‑end.

    Args:
        run_id (str, optional): Run identifier.  If None, a new run ID is
            generated automatically.
        seed (int): Random seed to use for deterministic operations.
    """
    # NOTE: Determine run ID and set seed for reproducibility
    if run_id is None:
        run_id = _generate_run_id()
    random.seed(seed)
    import numpy as np
    np.random.seed(seed)
    # Step status tracking
    status: Dict[str, str] = {}
    # NOTE: Execute Bronze layer
    try:
        run_bronze(run_id)
        status["bronze"] = "success"
    except Exception as e:
        status["bronze"] = f"failure: {e}"
        raise
    # NOTE: Execute Silver layer
    try:
        run_silver(run_id)
        status["silver"] = "success"
    except Exception as e:
        status["silver"] = f"failure: {e}"
        raise
    # NOTE: Execute Gold layer
    try:
        run_gold(run_id)
        status["gold"] = "success"
    except Exception as e:
        status["gold"] = f"failure: {e}"
        raise
    # NOTE: Execute EDA step
    try:
        run_eda(run_id)
        status["eda"] = "success"
    except Exception as e:
        status["eda"] = f"failure: {e}"
        raise
    # NOTE: Execute Feature Engineering step
    try:
        run_feature_engineering(run_id)
        status["feature_engineering"] = "success"
    except Exception as e:
        status["feature_engineering"] = f"failure: {e}"
        raise
    # NOTE: Execute Segmentation step
    try:
        run_segmentation(run_id, seed=seed)
        status["segmentation"] = "success"
    except Exception as e:
        status["segmentation"] = f"failure: {e}"
        raise
    # Generate final report regardless of previous failures
    # NOTE: Execute Final Report generation
    try:
        run_final_report(run_id)
        status["final_report"] = "success"
    except Exception as e:
        status["final_report"] = f"failure: {e}"
        raise
    # Write manifest and data policy
    _write_run_manifest(run_id, seed, status)
    _write_data_policy(run_id)


# NOTE: Command‑line interface wrapper
def main() -> None:
    """
    CLI wrapper for running the pipeline.
    """
    parser = argparse.ArgumentParser(description="Run the full data pipeline")
    parser.add_argument("--run-id", dest="run_id", default=None, help="Existing run ID to reuse")
    parser.add_argument("--seed", dest="seed", default=42, type=int, help="Random seed for deterministic operations")
    args = parser.parse_args()
    run_pipeline(run_id=args.run_id, seed=args.seed)


if __name__ == "__main__":
    main()
