# Artifact Contract

This document defines the required structure of the run folder created by the Golden Path.  Adhering to this contract ensures that downstream consumers and validation tests can reliably locate and interpret pipeline outputs.

## Root Layout

Each execution of the pipeline produces a unique `run_id`.  All artifacts are written to:

```
artifacts/runs/<run_id>/
```

Within this directory the following sub‑directories and files MUST exist:

### `_meta/`

| File | Description |
|------|-------------|
| `run_manifest.json` | Top‑level metadata for the run: run_id, seed, input file list with checksums, execution timestamps (UTC), git revision (if available) and status of each pipeline step. |
| `data_policy.json` | GDPR data policy describing personal fields, pseudonymisation and removal decisions, and a hash of the pseudonymisation salt. |

### `bronze/`

| Path | Description |
|------|-------------|
| `data/*.csv` | Byte‑for‑byte copies of raw CRM/ERP CSVs. |
| `data/metadata.yaml` | Metadata for the bronze run (per‑file statistics, ingestion state). |
| `reports/elt_report.html` | Human‑readable report summarising bronze load results. |

### `silver/`

| Path | Description |
|------|-------------|
| `data/*.csv` | Cleaned, standardised tables matching the bronze grain. |
| `data/metadata.yaml` | Metadata for the silver run (rows in/out, schema changes). |
| `reports/elt_report.html` | Silver load report. |

### `gold/`

| Path | Description |
|------|-------------|
| `data/*.csv` | Business marts: dimensions, fact, aggregates and wide table. |
| `metadata.yaml` | Metadata for the gold run (marts built, rows, schemas, errors). |
| `reports/gold_report.html` | Human‑readable gold report. |

### `step1_eda/`

| Path | Description |
|------|-------------|
| `data/eda_summary.json` | JSON containing aggregated statistics per table (counts, missing values, unique values). |
| `reports/eda_report.md` | Narrative EDA report. |

### `step2_feature_engineering/`

| Path | Description |
|------|-------------|
| `data/customer_features.csv` | Engineered features for each (pseudonymised) customer. |
| `reports/feature_dictionary.md` | Description of engineered features, including formulas and rationale. |

### `step3_segmentation/`

| Path | Description |
|------|-------------|
| `data/customer_segments.csv` | Mapping of pseudonymised customer identifier to cluster label. |
| `_meta/model_metadata.json` | Parameters used for clustering: algorithm, number of clusters, seed, feature list. |
| `reports/segmentation_report.md` | Analysis of clusters: sizes, centroids, top differentiating features. |

### `reports/`

| File | Description |
|------|-------------|
| `final_expose.md` | Executive summary covering pipeline status, data quality observations, segmentation highlights and recommendations. |
