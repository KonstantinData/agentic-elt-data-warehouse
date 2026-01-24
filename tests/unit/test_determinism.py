"""
Test deterministic behaviour of the segmentation step.

This test verifies that running the segmentation step twice with the
same seed and identical inputs yields identical cluster assignments.
"""

import uuid
from pathlib import Path
from src.pipeline.golden_path import run_pipeline
import csv


def load_segments(run_id: str) -> list[str]:
    path = Path("artifacts") / "runs" / run_id / "step3_segmentation" / "data" / "customer_segments.csv"
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row["segment"] for row in reader]


def test_deterministic_segmentation(tmp_path):
    run_id1 = f"det_{uuid.uuid4().hex[:8]}"
    run_id2 = f"det_{uuid.uuid4().hex[:8]}"
    seed = 101
    run_pipeline(run_id=run_id1, seed=seed)
    run_pipeline(run_id=run_id2, seed=seed)
    segments1 = load_segments(run_id1)
    segments2 = load_segments(run_id2)
    assert segments1 == segments2