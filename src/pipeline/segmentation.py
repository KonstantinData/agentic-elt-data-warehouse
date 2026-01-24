"""
File: src/pipeline/segmentation.py

Purpose:
  Implements Step 5: Segmentation & Clustering.  This step takes the
  engineered customer features and uses k‑means clustering to assign
  each customer to a segment.  It outputs both the assignments and
  summary metrics describing the clusters.  All randomness is
  controlled via a single seed to ensure deterministic results.

Why it exists:
  Segmentation allows the business to understand groups of customers
  with similar behaviours.  Deterministic clustering ensures that
  reruns of the pipeline with the same inputs and seed yield identical
  segment assignments.

Inputs:
  - `customer_features.csv` produced by the feature engineering step.

Outputs:
  - `customer_segments.csv` with `customer_hash` and `segment` columns.
  - `model_metadata.json` capturing the algorithm parameters and feature list.
  - `segmentation_report.md` summarising cluster sizes and average feature values per cluster.

Step:
  This module belongs to the segmentation and clustering step and must
  be executed after feature engineering.
"""

import csv
import json
from pathlib import Path
from typing import List, Dict
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# NOTE: Execute the segmentation step for a given run ID
def run_segmentation(run_id: str, seed: int = 42, n_clusters: int = 3) -> None:
    """
    Entry point for the segmentation step.

    Args:
        run_id (str): Unique identifier for this pipeline run.
        seed (int): Random seed for clustering.
        n_clusters (int): Number of clusters to compute.
    """
    # NOTE: Locate feature data and set up output directories
    project_root = Path(__file__).resolve().parents[2]
    fe_data_dir = project_root / "artifacts" / "runs" / run_id / "step2_feature_engineering" / "data"
    seg_dir = project_root / "artifacts" / "runs" / run_id / "step3_segmentation"
    seg_data_dir = seg_dir / "data"
    seg_meta_dir = seg_dir / "_meta"
    seg_reports_dir = seg_dir / "reports"
    seg_data_dir.mkdir(parents=True, exist_ok=True)
    seg_meta_dir.mkdir(parents=True, exist_ok=True)
    seg_reports_dir.mkdir(parents=True, exist_ok=True)
    # Read feature table
    with open(fe_data_dir / "customer_features.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        customer_hashes: List[str] = []
        feature_vectors: List[List[float]] = []
        for row in reader:
            customer_hashes.append(row["customer_hash"])
            feature_vectors.append([
                float(row["total_qty"]),
                float(row["total_revenue"]),
                float(row["avg_unit_price"]),
                float(row["num_transactions"]),
                float(row["num_distinct_products"]),
            ])
    X = np.array(feature_vectors)
    # Standardise features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    # NOTE: Set seed for reproducibility
    kmeans = KMeans(n_clusters=n_clusters, random_state=seed, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    # Write segments
    with open(seg_data_dir / "customer_segments.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["customer_hash", "segment"])
        for cust, seg in zip(customer_hashes, clusters):
            writer.writerow([cust, str(int(seg))])
    # Write model metadata
    model_meta = {
        "algorithm": "kmeans",
        "n_clusters": n_clusters,
        "seed": seed,
        "features": [
            "total_qty",
            "total_revenue",
            "avg_unit_price",
            "num_transactions",
            "num_distinct_products",
        ],
    }
    with open(seg_meta_dir / "model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(model_meta, f, indent=2)
    # Create report summarising clusters
    report_lines: List[str] = ["# Segmentation Report", "", f"Run ID: {run_id}", ""]
    # Compute cluster sizes and means
    cluster_sizes: Dict[int, int] = {i: 0 for i in range(n_clusters)}
    cluster_sums: Dict[int, List[float]] = {i: [0.0] * len(model_meta["features"]) for i in range(n_clusters)}
    for seg, vec in zip(clusters, feature_vectors):
        cluster_sizes[seg] += 1
        for idx, val in enumerate(vec):
            cluster_sums[seg][idx] += val
    report_lines.append("## Cluster Summary")
    for seg in range(n_clusters):
        size = cluster_sizes[seg]
        report_lines.append(f"### Cluster {seg}")
        report_lines.append(f"- Size: {size}")
        if size > 0:
            means = [cluster_sums[seg][i] / size for i in range(len(model_meta["features"]))]
            for feature_name, mean_val in zip(model_meta["features"], means):
                report_lines.append(f"- {feature_name} (avg): {mean_val:.2f}")
        report_lines.append("")
    (seg_reports_dir / "segmentation_report.md").write_text("\n".join(report_lines), encoding="utf-8")
