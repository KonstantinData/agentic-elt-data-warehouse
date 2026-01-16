# Generated Outputs & ELT Artifacts

The **`artifacts/`** directory is the canonical storage location for all outputs produced by the ELT pipeline. It hosts persistent artifacts from the Bronze, Silver, Gold, Machine Learning workflows, and global reports. Each run — where applicable — is stored in a timestamped, hash-tagged subfolder to ensure traceability and reproducibility.

The directory structure is as follows:

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
│   ├── planning/
│   │   └── <timestamp>_#<hash>/
│   │       ├── data/
│   │       └── reports/
│   └── marts/
│       └── <timestamp>_#<hash>/
│           ├── _meta/
│           ├── data/
│           ├── reports/
│           └── run_log.txt
├── ml/
└── reports/
```

### Bronze Layer Outputs

**Path Pattern:**

```
artifacts/bronze/<timestamp>_#<hash>/
```

**Contents:**

* `data/` — Raw ingested datasets stored as snapshots (e.g., CSV, Parquet).
* `reports/` — Metadata about the run (schemas, row counts, profiling outputs, timing).

**Purpose:**
Captures the **initial ingestion stage** of all source data with minimal transformation. This layer is the basis for Silver transformation and must be immutable once produced.

---

### Silver Layer Outputs

**Path Pattern:**

```
artifacts/silver/<timestamp>_#<hash>/
```

**Contents:**

* `data/` — Cleaned, standardized, and typed data sets.
* `reports/` — Diagnostics and validation artifacts related to transformation.
* `tmp/` — Temporary artifacts or staging files used by transformation logic (ephemeral).

**Purpose:**
Holds **standardized data** that has been cleansed and prepared for analytical use or further transformation in Gold.

---

### Gold Layer Outputs

Gold is subdivided into **planning outputs** and **final mart outputs**:

#### Gold Planning

**Path Pattern:**

```
artifacts/gold/planning/<timestamp>_#<hash>/
```

**Contents:**

* `data/` — Intermediate plan artifacts (strategy datasets, mapping candidates).
* `reports/` — Metadata and diagnostics from the Gold planning step.

**Purpose:**
Stores outputs from the Gold layer planning process (e.g., definitions and evaluation artifacts that inform the final mart build).

---

#### Gold Marts

**Path Pattern:**

```
artifacts/gold/marts/<timestamp>_#<hash>/
```

**Contents:**

* `_meta/` — Run metadata including schema definitions, lineage mappings, and run configuration.
* `data/` — Gold-level outputs (models, business tables, aggregated datasets).
* `reports/` — Diagnostics, profiling outputs, and summaries specific to this mart run.
* `run_log.txt` — Execution log for this Gold run.

**Purpose:**
Contains **business-ready artifacts** produced by the final Gold layer build, intended for consumption by analytics, BI dashboards, ML pipelines, and reporting workflows.

---

### Machine Learning Artifacts

```
artifacts/ml/
```

**Contents and Use:**
Artifacts specific to machine learning workflows (e.g., feature engineering outputs, training/test snapshots, ML-specific data artifacts). The internal structure may evolve depending on use cases.

**Purpose:**
Holds ML-oriented data and outputs derived from Silver or Gold layers.

---

### Cross-Layer Reports

```
artifacts/reports/
```

**Contents:**
High-level reports and dashboards that synthesize information across Bronze, Silver, and Gold runs. These can include:

* Composite KPI summaries
* Data quality scorecards
* Lineage and profiling dashboards
* Cross-run diagnostics

**Purpose:**
Provides **centralized visibility** into the health, performance, and state of the ELT pipelines across all layers.

---

### Naming Convention

All **timestamped run folders** follow the format:

```
YYYYMMDDHHMMSS_#<hash>
```

This ensures:

* Clear chronological ordering
* Traceability back to code and commit versions
* Idempotent reproducibility of runs

---

### Best Practices

* **Do not modify** artifacts after creation; treat timestamped folders as immutable snapshots.
* Use metadata in `reports/` and `_meta/` folders to validate and audit runs.
* Enforce retention policies based on governance or storage constraints.
* Only remove `tmp/` or ephemeral folders according to automated cleanup policies.
