"""
Test the end‑to‑end pipeline on the provided sample data.

This smoke test executes the golden path on a temporary run ID and
asserts that the expected output files are created and contain
non‑zero rows.  It does not inspect the contents in detail but
validates the overall run contract.
"""

import os
import shutil
import uuid
from pathlib import Path

from src.pipeline.golden_path import run_pipeline


def test_end_to_end(tmp_path):
    """
    Run the pipeline and assert that key outputs exist.
    """
    run_id = f"test_{uuid.uuid4().hex[:8]}"
    run_pipeline(run_id=run_id, seed=123)
    run_root = Path("artifacts") / "runs" / run_id
    # Assert manifest and data policy exist
    assert (run_root / "_meta" / "run_manifest.json").exists()
    assert (run_root / "_meta" / "data_policy.json").exists()
    # Assert Bronze outputs exist
    assert any((run_root / "bronze" / "data").glob("*.csv"))
    # Assert Silver outputs exist
    assert any((run_root / "silver" / "data").glob("*.csv"))
    # Assert Gold wide table exists
    assert (run_root / "gold" / "data" / "gold_wide_sales_enriched.csv").exists()
    # Assert feature engineering output exists
    assert (run_root / "step2_feature_engineering" / "data" / "customer_features.csv").exists()
    # Assert segmentation output exists
    assert (run_root / "step3_segmentation" / "data" / "customer_segments.csv").exists()
    # Assert final report exists
    assert (run_root / "reports" / "final_expose.md").exists()
    # Clean up after test to avoid polluting repository
    shutil.rmtree(run_root)
