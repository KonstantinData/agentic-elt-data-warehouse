# Agentic ELT Data Warehouse (Enhanced)

This repository contains a deterministic, audit‑friendly ELT/analytics pipeline for a mid‑sized German company.  The pipeline ingests raw CRM and ERP data, cleans and standardises it, builds star‑schema business marts, performs exploratory data analysis (EDA), engineers features, runs customer segmentation using k‑means clustering and produces a final exposé report.  All outputs are stored in a unified run directory under `artifacts/runs/<run_id>/` which acts as the single source of truth for a pipeline execution.

## Golden Path

The **Golden Path** is a single command that runs the entire pipeline end‑to‑end and produces the final exposé report.  It executes the following steps in sequence:

1. **Bronze layer** – copies raw CSV files from `raw/source_crm` and `raw/source_erp` into the run folder under `bronze/data/` and records ingestion metadata.
2. **Silver layer** – cleans and standardises the bronze tables (trimming whitespace, normalising dates and numerics, harmonising codes) and writes them to `silver/data/`.
3. **Gold layer** – builds business marts (dimensions, facts and aggregated KPI tables) from the silver tables and writes them to `gold/data/`.
4. **EDA** – generates summary statistics and an EDA report without exposing personally identifiable information (PII).
5. **Feature engineering** – aggregates customer‑level features from the gold marts and writes a feature table used for clustering.
6. **Segmentation & clustering** – applies deterministic k‑means clustering to segment customers and writes cluster assignments along with model metadata and a segmentation report.
7. **Final exposé** – compiles an executive‑ready summary covering data quality, segmentation highlights and recommended next steps.

To execute the Golden Path, run the following command from the project root:

```bash
python src/pipeline/golden_path.py --run-id <optional_custom_id> --seed 42
```

If no `--run-id` is provided a new timestamp‑based run identifier is generated automatically.  The optional `--seed` parameter controls all stochastic elements (e.g. k‑means initialisation) to ensure deterministic outputs across runs.

## Unified Artifact Contract

Each pipeline run writes its outputs into `artifacts/runs/<run_id>/`.  The following structure is produced:

```
artifacts/runs/<run_id>/
├── _meta/
│   ├── run_manifest.json       # metadata: run_id, seed, input checksums, timestamps, status
│   └── data_policy.json        # GDPR data policy: detected personal fields and how they were handled
├── bronze/
│   ├── data/*.csv              # raw CSV copies (byte‑for‑byte)
│   ├── reports/bronze_report.md # bronze load report
│   └── _meta/bronze_metadata.yaml      # bronze run metadata
├── silver/
│   ├── data/*.csv              # cleaned tables
│   ├── reports/silver_quality_report.md # silver quality report
│   └── _meta/silver_metadata.yaml      # silver run metadata
├── gold/
│   ├── data/*.csv              # star schema tables and aggregates
│   ├── reports/gold_marts_report.md
│   └── _meta/gold_metadata.yaml
├── step1_eda/
│   ├── data/eda_summary.json   # summary statistics (no PII)
│   └── reports/eda_report.md   # narrative EDA report
├── step2_feature_engineering/
│   ├── data/customer_features.csv # engineered feature table
│   └── reports/feature_dictionary.md # description of engineered features
├── step3_segmentation/
│   ├── data/customer_segments.csv   # pseudonymised customer id with cluster assignment
│   ├── _meta/model_metadata.json    # algorithm parameters, seed, feature list
│   └── reports/segmentation_report.md # cluster sizes and differentiators
└── reports/
    └── final_expose.md         # executive summary report
```

All personally identifying columns (e.g. first name, last name, business key) are either removed or pseudonymised via a stable hash using a secret salt stored in a local `.env` file.  The `data_policy.json` records which columns were considered personal and how they were handled.

## GDPR and Data Safety

The pipeline is designed to be **GDPR‑safe by default**.  Raw inputs may include customer names and business identifiers.  During the Silver and Gold stages direct identifiers are retained only in the protected run folder.  Subsequent steps (feature engineering, clustering, final reports) drop or hash these identifiers.  Tests enforce that no PII appears in final outputs.

For details on the data policy and pseudonymisation methods see [`docs/data_policy.md`](docs/data_policy.md).

## Documentation

This repository uses [`docs/`](docs/) as the single source of truth for architecture, data policy, and runbook information.  Key documents include:

- [`docs/architecture/golden_path.md`](docs/architecture/golden_path.md) – detailed description of each pipeline step.
- [`docs/architecture/artifact_contract.md`](docs/architecture/artifact_contract.md) – specification of the unified run folder layout.
- [`docs/architecture/ml_segmentation_flow.md`](docs/architecture/ml_segmentation_flow.md) – design of the ML segmentation pipeline.
- [`docs/runbook.md`](docs/runbook.md) – how to run the pipeline locally, validate results, and troubleshoot.

## Running Tests

Tests live under `tests/` and are executed via `pytest`.  To run the full test suite and an end‑to‑end smoke test, execute:

```bash
pytest -q
```

CI workflows (see `.github/workflows/ci.yml`) also run notebooks, perform placeholder scans, and enforce the documentation standard described in this README.
