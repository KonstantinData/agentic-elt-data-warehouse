"""
Test that final output tables do not contain direct personal identifiers.

The final outputs should not include raw first names or last names from the
input data.  This test runs a pipeline and checks the header and
contents of customer features and segments tables to ensure no
identifiers leak.
"""

import csv
import uuid
from pathlib import Path
from src.pipeline.golden_path import run_pipeline


def test_no_personal_identifiers(tmp_path):
    run_id = f"pii_{uuid.uuid4().hex[:8]}"
    run_pipeline(run_id=run_id, seed=1234)
    # Check headers
    features_path = Path("artifacts") / "runs" / run_id / "step2_feature_engineering" / "data" / "customer_features.csv"
    with open(features_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert "firstname" not in header
        assert "lastname" not in header
        for row in reader:
            for val in row:
                assert val not in {"Alice", "Bob", "Carla", "David", "Eva"}
    segments_path = Path("artifacts") / "runs" / run_id / "step3_segmentation" / "data" / "customer_segments.csv"
    with open(segments_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header_seg = next(reader)
        assert "firstname" not in header_seg
        assert "lastname" not in header_seg
        for row in reader:
            for val in row:
                assert val not in {"Alice", "Bob", "Carla", "David", "Eva"}