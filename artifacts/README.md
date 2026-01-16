# Generated Outputs & ELT Artifacts

This folder contains all generated artifacts from ELT runs — including  **Bronze** ,  **Silver** , and **Gold** layer outputs, as well as reports and supporting files. Each run produces timestamped folders that encapsulate both data and metadata for reproducibility, auditing, and downstream use.

---

## Table of Contents

1. Purpose
2. Structure
3. Bronze Layer Artifacts
4. Silver Layer Artifacts
5. Gold Layer Artifacts
6. Reports
7. Temporary & Support Files
8. Best Practices
9. Cleanup & Retention

---

## 1. Purpose

The `artifacts/` directory serves as the canonical storage location for outputs from your ELT pipeline. It is structured to:

* **Separate layers** (Bronze, Silver, Gold) clearly
* **Version each run** by timestamp + hash
* **Store both data and descriptive metadata**
* **Make results reproducible and auditable**

This layout supports both manual inspection and automated consumption by BI/ML workflows.

---

## 2. Directory Structure

```
artifacts/
├── bronze/
│   └── <timestamp>_#<hash>/
│       ├── data/
│       └── reports/
├── silver/
│   └── <timestamp>_#<hash>/
│       ├── data/
│       ├── reports/
│       └── tmp/
├── gold/
│   ├── marts/
│   ├── planning/
│   └── ml/
└── reports/
```

Each section below describes the contents and purpose of these folders.

---

## 3. Bronze Layer Artifacts

Path:

```
artifacts/bronze/<timestamp>_#<hash>/
```

### Contents

* `data/`:
  Raw snapshots of ingested datasets, cleaned only to the extent necessary for persistence. Typically includes CSV/Parquet files.
* `reports/`:
  Run reports and metadata (e.g., schemas, row counts, timing). Useful for lineage tracking and data quality.

### Purpose

The Bronze layer represents **raw ingestion** results — the first persist phase after reading source data. This layer should be treated as immutable once generated.

---

## 4. Silver Layer Artifacts

Path:

```
artifacts/silver/<timestamp>_#<hash>/
```

### Contents

* `data/`:
  Standardized/cleaned tables suitable for analytical use or further processing.
* `reports/`:
  Metadata and diagnostics related to transformations — profiling statistics, row counts, and validation reports.
* `tmp/`:
  Temporary staging files used during processing.

### Purpose

Silver outputs are **cleaned, typed, and validated** versions of Bronze data. They serve as the foundation for business logic and aggregation.

---

## 5. Gold Layer Artifacts

Path:

```
artifacts/gold/
```

### Subdirectories

* `planning/`:
  Stores intermediate artifacts from Gold layer planning — configuration files, build plans, mappings.
* `marts/`:
  Final business-ready tables and models (e.g., dimensional marts, aggregated views).
* `ml/`:
  Artifacts tailored for machine learning workflows — features, training snapshots, etc.

### Purpose

Gold layer artifacts represent **business-ready models** used directly by reporting systems, dashboards, and ML models.

---

## 6. Reports

```
artifacts/reports/
```

This directory aggregates **global run reports** across layers — e.g., summaries, cross-layer dashboards, KPIs, and centralized diagnostics. It is not tied to any single timestamped run.

Reports may include:

* HTML dashboards
* CSVs with lineage/metrics
* Consolidated logs

---

## 7. Temporary & Support Files

Temporary files under Silver (`tmp/`) are typically ephemeral and may be cleaned between runs.

---

## 8. Best Practices

### Immutable Runs

Each run’s folder is **timestamped and hashed** to ensure immutability and traceability.

Do not modify existing run artifacts manually. Instead, generate a new run for any changes.

### Naming Conventions

```
<YYYYMMDDHHMMSS>_#<commit|hash>
```

This pattern ensures chronological ordering and linkage to version control.

### Metadata

Always inspect the `reports/` metadata for:

* Row counts
* Schema details
* Validation results

---

## 9. Cleanup & Retention

Depending on storage policies, you may want to implement:

* Archival policies for old runs
* Storage quotas per layer
* Automatic cleanup of `tmp/` directories

Automated cleanups should preserve at least the most recent **N runs** in each layer.

---

## Summary of Layers

| Layer   | Location                                 | Purpose                                  |
| ------- | ---------------------------------------- | ---------------------------------------- |
| Bronze  | `artifacts/bronze/<timestamp>_#<hash>` | Raw ingestion snapshots                  |
| Silver  | `artifacts/silver/<timestamp>_#<hash>` | Cleaned/standardized tables              |
| Gold    | `artifacts/gold/`                      | Business models & features (marts, ML)   |
| Reports | `artifacts/reports/`                   | Consolidated diagnostics & run summaries |
