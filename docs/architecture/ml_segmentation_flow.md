# ML Segmentation Flow

This document describes the machine learning (ML) workflow implemented in the segmentation and clustering stage of the Golden Path.

## Objective

The goal of segmentation is to group customers into homogeneous clusters based on their purchasing behaviour and demographic attributes.  These segments can then be used for targeted marketing, resource allocation and business planning.

## Pipeline Steps

1. **Feature Selection** – Features are engineered in the preceding feature engineering stage.  Only non‑identifying, numeric features are used for clustering (e.g. total revenue, average order value, number of distinct products, recency).  Categorical attributes are one‑hot encoded.
2. **Scaling** – Since k‑means is sensitive to feature scales, all features are standardised using `sklearn.preprocessing.StandardScaler`.
3. **Clustering** – K‑means clustering is performed using `sklearn.cluster.KMeans` with a fixed `random_state` equal to the run seed.  The number of clusters is configurable via CLI (default `5`).
4. **Pseudonymisation** – Customer identifiers are hashed using SHA‑256 with a secret salt.  The resulting hash is used as the stable key in the output `customer_segments.csv`.
5. **Reporting** – A report is generated summarising cluster sizes, centroid values for each feature and the top differentiating features.  This report is written to `reports/segmentation_report.md`.  Model parameters and the feature list are recorded in `model_metadata.json`.

## Determinism

To ensure deterministic segmentation results across runs, the clustering algorithm is configured with a fixed `random_state`.  The seed is passed through the Golden Path CLI via `--seed`.  All pseudonymisation also uses the same salt across runs so that customers can be tracked consistently over time without revealing their identity.
