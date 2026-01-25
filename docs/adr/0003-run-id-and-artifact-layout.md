# 0003 – Run ID & Artifact Layout

*Status:* Accepted

## Context

The agentic ELT pipeline generates logs, outputs, and metadata across multiple layers (Bronze, Silver, Gold). Without a consistent structure, troubleshooting and audits become expensive and unreliable. Each layer has specific run_id generation logic that must be documented.

## Decision

Each pipeline execution receives a unique **Run ID** following the pattern `YYYYMMDD_HHMMSS_#<hex>`. Artifacts are stored in a consistent directory structure keyed by Run ID and layer.

### Run ID Generation Logic

- **Bronze Layer**: Generates initial run_id with timestamp and random hex suffix
  - Format: `20260125_204110_#527f1cea`
  - Location: `artifacts/bronze/<run_id>/`

- **Silver Layer**: Creates new run_id with fresh timestamp but **same suffix** as Bronze
  - Format: `20260125_204143_#527f1cea` (new timestamp, same `#527f1cea`)
  - Location: `artifacts/silver/<silver_run_id>/`
  - Purpose: Maintains lineage while allowing multiple Silver runs per Bronze

- **Gold Layer**: Uses **Bronze run_id** for consistency across business marts
  - Format: `20260125_204110_#527f1cea` (same as Bronze)
  - Location: `artifacts/gold/marts/<bronze_run_id>/`
  - Purpose: Ensures business marts are consistently grouped

- **Orchestrator**: Generates own run_id for execution tracking
  - Location: `artifacts/orchestrator/<orchestrator_run_id>/`
  - Contains logs for all pipeline steps

### Directory Structure

```
artifacts/
├── bronze/<run_id>/
│   ├── data/*.csv
│   └── reports/elt_report.html
├── silver/<silver_run_id>/
│   ├── data/*.csv
│   └── reports/elt_report.html
├── gold/marts/<bronze_run_id>/
│   ├── data/*.csv
│   └── reports/gold_report.html
├── orchestrator/<orchestrator_run_id>/
│   └── logs/*.log
└── reports/<orchestrator_run_id>/
    ├── summary_report.md
    └── team_reports/*.md
```

## Rationale

* **Auditability:** Results can be traced to specific runs across all layers
* **Lineage tracking:** Suffix consistency enables Bronze→Silver→Gold traceability
* **Operational efficiency:** Logs and outputs are discoverable quickly
* **Compliance readiness:** Supports retention and audit requirements
* **Multi-run support:** Allows multiple Silver runs per Bronze without conflicts

## Consequences

* All jobs must follow naming and storage conventions
* Improves long-term observability and SLA reporting
* Enables incremental processing and data lineage tracking
* Supports agentic pipeline debugging and troubleshooting
