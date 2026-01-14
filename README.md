# Data Warehouse Project (Python ELT-First)

This project implements a **local, Python-driven Data Warehouse pipeline** using raw CSV sources from **CRM** and **ERP**, transforming them through a controlled ELT workflow into a reproducible **Bronze layer**, and exposing outputs for analysis, reporting, and downstream ML.

All processing is done in **Python**, using standard libraries for ingestion, logging, metadata, and reporting. There is **no external database required** for the Bronze layer.

---

## Table of Contents

1. [Overview](#overview)  
2. [Architecture](#architecture)  
3. [Getting Started](#getting-started)  
4. [File & Folder Structure](#file--folder-structure)  
5. [Bronze ELT Process (Python)](#bronze-elt-process-python)  
6. [Artifacts & Outputs](#artifacts--outputs)  
7. [Reporting & Metadata](#reporting--metadata)  
8. [Extending to Silver & Gold](#extending-to-silver--gold)  
9. [Dependencies](#dependencies)  
10. [Contributing](#contributing)  
11. [License](#license)

---

## Overview

This repository implements a **data warehouse pipeline** using plain Python and standard data libraries:

- **Extract** raw source CSV files (CRM + ERP)
- **Load** them into a stable Bronze staging layer (as filesystem snapshots)
- **Track** lineage, durations, and audit metadata
- **Provide** reusable artifacts for analysis, ML, or reporting

This ELT approach avoids dependency on a SQL engine at the Bronze stage, enabling lightweight reproducibility on local machines or cloud VMs.

---

## Architecture

The architecture follows a **Medallion design**:

Sources (raw CSVs)
↓
Bronze Layer (Python ELT snapshots)
↓
Silver Layer (clean, standardized)
↓
Gold Layer (business-ready analytics/aggregates)
↓
Consume (BI, Reporting, SQL/ML)

yaml
Code kopieren

For this phase, the focus is on **Bronze Layer** generation using Python.

---

## Getting Started

**Prerequisites**
- Python 3.10+
- git

**Clone the Repo**
```bash
git clone https://github.com/KonstantinData/data-warehouse.git
cd data-warehouse
Create & Activate Virtual Environment

bash
Code kopieren
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows
Install Dependencies

bash
Code kopieren
pip install -r requirements.txt
File & Folder Structure
graphql
Code kopieren
data-warehouse/
├── analytics/                     # BI artifacts & definitions
├── artifacts/                    # Built outputs and snapshots
│   ├── bronze/
│   │   ├── elt/                 # Bronze runs (timestamped)
│   │   └── README.md
│   ├── silver/                  # Silver layer placeholders
│   ├── gold/                    # Gold layer placeholders
│   ├── reports/                 # Reporting artifacts
│   └── tmp/                     # Temporary intermediate
├── configs/                     # Configuration templates
├── docs/                        # Architecture & standards docs
├── ml/                          # ML experiments (PyTorch)
├── raw/                         # Raw source files
│   ├── source_crm/
│   └── source_erp/
├── scripts/                    # Support scripts
├── src/                        # Python ELT code
│   └── elt_runner.py
├── tests/                     # Test placeholders
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── README.md
└── LICENSE
Bronze ELT Process (Python)
The Bronze layer is generated exclusively via Python. No SQL engine or external DB is used for snapshotting.

How it Works
Discover raw files under raw/source_crm and raw/source_erp.

Read CSVs into pandas DataFrames.

Time each load (duration, rows).

Write snapshots into a versioned output directory under:

php-template
Code kopieren
artifacts/bronze/elt/<timestamp>_#<random>/
Save:

original CSV copies

metadata.yaml with schema + row counts

run_log.txt with success/failure and durations

simple HTML summary report

Run ELT
bash
Code kopieren
python src/elt_runner.py
Each run yields a unique folder for reproducibility.

Artifacts & Outputs
Each Bronze run produces:

powershell
Code kopieren
artifacts/bronze/elt/
├── 20260114_2249_#9abcdef/
│   ├── data/
│   │   ├── cst_info.csv
│   │   ├── prd_info.csv
│   │   ├── sales_details.csv
│   │   ├── CST_AZ12.csv
│   │   ├── LOC_A101.csv
│   │   ├── PX_CAT_G1V2.csv
│   │   ├── metadata.yaml
│   │   └── run_log.txt
│   └── reports/
│       └── elt_report.html
What’s Inside
Component	Description
data/*.csv	Snapshot copies of raw source files
metadata.yaml	Per-file schema and row counts
run_log.txt	Process logs & durations
reports/elt_report.html	Human-readable run summary

Reporting & Metadata
The HTML report includes:

Run start and end timestamps

Per-file duration

Status (OK or FAILED)

Row counts

Error messages (if any)

The metadata.yaml file contains:

Run ID and timestamp

Source file list

Schema for each file

Duration metrics

These artifacts support lineage review and audit.

Extending to Silver & Gold
While this phase captures raw snapshots, you can build:

Silver Layer (clean/standardized)
Normalize column names

Convert data types

Join ERP + CRM to enrich customer and product dimensions

Derived columns (e.g., age from birthdates)

Output to artifacts/silver/

Gold Layer (business logic)
Aggregations (e.g., sales per product, sales per country)

KPI tables for BI

Output to artifacts/gold/

Silver/Gold code can also be Python modules similar to the Bronze design.

Dependencies
The pipeline uses:

text
Code kopieren
pandas>=2.0.3
python-dotenv>=1.0.0
PyYAML>=6.0
Jinja2>=3.0
torch>=2.1.0
torchvision>=0.15.2
scikit-learn>=1.3.0
Install with:

bash
Code kopieren
pip install -r requirements.txt
Testing
Tests are located under:

Code kopieren
tests/
They can be run with pytest:

bash
Code kopieren
pytest
Contributing
Fork the repo

Create a feature branch

Add tests and code

Open a pull request

Follow code style via pre-commit hooks (if enabled).

License
This project is licensed under the MIT License.

Contact
For questions or suggestions, open an issue or reach out to the author in this repository.
