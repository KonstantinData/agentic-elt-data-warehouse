
# Tableau Analytics Workspace *(Planned)*

This folder is designated to organize and house **Tableau analytics artifacts** for the data warehouse project. It does not yet contain production assets — it represents a planned workspace for building dashboards, data sources, extracts, documentation, and analytics best practices.

---

## Project Purpose

The goal of the `analytics/tableau/` directory is to provide a structured environment for developing  **Tableau visual analytics** , including:

* Business dashboards based on Silver and Gold data layers
* Shared, versioned Tableau Data Sources
* Extracts for performance optimization
* Documentation for analytics standards and usage

As the ELT workflows mature, this folder will evolve into the central repository for BI artifacts.

---

## Planned Directory Structure

The following structure is proposed for this workspace:

```
analytics/tableau/
├── workbooks/            # Excel, TWBX, TWB Tableau workbooks
├── datasources/          # Published Tableau data sources (TDS/TDSX)
├── extracts/             # Tableau Hyper extracts for performance
├── docs/                 # Documentation and guidelines
├── templates/            # Starter templates for dashboards
└── .gitkeep              # Placeholder until content is added
```

---

## What Will Go Into Each Folder

### `workbooks/`

Reserved for finalized or in-development Tableau workbook files:

* `.twbx` — Packaged workbooks with embedded extracts
* `.twb` — Workbook metadata only

These will be organized by subject area (e.g., sales, operations, finance) and version number as dashboards are constructed.

---

### `datasources/`

This folder will contain:

* **Tableau Data Source Definitions** (`.tds`, `.tdsx`)
* Standardized connections to Silver and Gold layer artifacts
* Shared structures supporting multiple workbooks

---

### `extracts/`

Planned to hold:

* Tableau Hyper extract files (`.hyper`) generated from Silver or Gold sources
* Versioned extracts aligned with data releases

Extracts will help with performance and offline analytics.

---

### `docs/`

Documentation will be developed here, including:

* Analytics standards and naming conventions
* How-to guides for updating dashboards
* Field definitions and a Tableau data dictionary
* Release & versioning strategy

Example future files:

```
analytics/tableau/docs/
├── how_to_update_dashboards.md
├── tableau_data_dictionary.md
├── naming_conventions.md
└── release_process.md
```

---

### `templates/`

Starter templates for:

* Standard visual styles and filters
* Month/quarter/year parameter configurations
* Baseline dashboards aligned with business KPIs

Templates will accelerate new workbook development and enforce consistency.

---

## Future Usage Scenarios

Once implemented, this folder will support:

### Dashboard Development

Analysts will develop workbooks against stable Silver/Gold datasets, and save them here with meaningful names and version tags.

### Versioning & Governance

Each analytic asset should be versioned consistently with ELT layer runs, e.g.:

```
sales_dashboard_v0.1_20260201.twbx
```

Tracking versions enables reproducibility and coordination with data releases.

### Documentation

Clear guidance will be published in `docs/` for:

* How analytics connect to layers
* How to refresh extracts
* Naming standards
* Publication workflows for Tableau Server or Cloud

---

## Naming & Versioning Principles *(Planned)*

Future naming conventions will follow a pattern for transparency:

| Asset Type  | Example Name                     |
| ----------- | -------------------------------- |
| Workbook    | `customer_retention_v0.1.twbx` |
| Data Source | `silver_sales_v0.1.tdsx`       |
| Extract     | `gold_marts_v0.1.hyper`        |

Each asset’s version should reflect milestone state in development.

---

## Implementation Roadmap *(Tentative)*

1. Initialize directory with subfolders and `.gitkeep` files
2. Publish first Tableau Data Sources connected to Gold layer
3. Create baseline dashboards (executive, operations, sales)
4. Document data dictionary and standards
5. Add extraction and refresh automation guidance

---

## Contribution Guidelines *(Planned)*

When working on this folder:

* Use descriptive asset names and version numbers
* Update documentation with each major addition
* Follow common UX and charting best practices
* Include a change log for significant updates

---

## Summary

This folder represents the future **Tableau analytics layer** of the project. It is planned but not yet populated. Over time, it will house structured BI content with clear documentation, versioning, and governance to support enterprise reporting.
