# Golden Path Architecture

The **Golden Path** is a deterministic, reproducible workflow that transforms raw CRM and ERP data into actionable insights.  It is composed of seven stages executed in sequence by `src/pipeline/golden_path.py`.

## Stages

### 1. Bronze Layer

Raw CSV files from `raw/source_crm` and `raw/source_erp` are copied verbatim into the run directory under `bronze/data/`.  The bronze loader records per‑file metadata (size, modification time, SHA‑256 checksum) and produces an HTML report summarising load status.  No transformations occur at this stage.

### 2. Silver Layer

The silver loader cleans and standardises each table individually:

- Trims whitespace and converts empty strings to `NA`.
- Normalises dates to ISO format (`YYYY-MM-DD`).
- Parses numeric columns and converts identifiers to nullable integers.
- Harmonises domain codes (e.g. gender values to `M`/`F`/`NA`).

The output tables remain at the same grain as the input but are schema‑consistent.  Metadata and an HTML report are produced for auditability.

### 3. Gold Layer

The gold layer builds a star‑schema data warehouse.  It reads silver tables and constructs:

- **Dimension tables** – customers, products and locations.
- **Fact table** – sales order lines.
- **Aggregated marts** – executive KPIs, product performance and geographic performance.
- **Wide table** – sales enriched with customer and product attributes.

Each mart is written as a separate CSV under `gold/data/` and accompanied by metadata and a report.

### 4. Exploratory Data Analysis (EDA)

The EDA step computes summary statistics (counts, missingness, distributions) for each gold mart.  It produces:

- `step1_eda/data/eda_summary.json` – JSON file containing aggregated metrics per table (no PII).
- `step1_eda/reports/eda_report.md` – markdown narrative describing data quality findings and anomalies.

### 5. Feature Engineering

Customer‑level features are engineered from the gold marts.  Examples include:

- Total revenue and total quantity across orders.
- Average order value.
- Number of distinct products purchased.
- Recency of last purchase.

The resulting table is written to `step2_feature_engineering/data/customer_features.csv` and documented in `feature_dictionary.md`.

### 6. Segmentation & Clustering

Using the engineered features, the pipeline applies k‑means clustering to segment customers.  The algorithm uses a fixed `seed` to ensure determinism.  Outputs include:

- `customer_segments.csv` – pseudonymised customer identifier with cluster assignment.
- `model_metadata.json` – clustering parameters, random seed and feature list.
- `segmentation_report.md` – cluster sizes, centroids and feature importances.

### 7. Final Exposé

A final narrative report (`reports/final_expose.md`) summarises the pipeline run: high‑level data quality, key insights from segmentation and recommended next steps.
