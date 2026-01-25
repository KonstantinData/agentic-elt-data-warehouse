# Golden Path Architecture

The **Golden Path** is a deterministic, reproducible workflow that transforms raw CRM and ERP data into actionable insights. It is composed of three main layers executed in sequence by `src/runs/orchestrator.py`.

## Architecture Overview

The pipeline follows a **Medallion Architecture** with three layers:
- **🥉 Bronze Layer**: Raw data ingestion
- **🥈 Silver Layer**: Data cleaning and standardization  
- **🥇 Gold Layer**: Business marts and analytics

## Layers

### 1. Bronze Layer (`src/runs/load_1_bronze_layer.py`)

Raw CSV files from `raw/source_crm` and `raw/source_erp` are copied verbatim into the run directory under `artifacts/bronze/<run_id>/data/`. The bronze loader records per‑file metadata (size, modification time, SHA‑256 checksum) and produces an HTML report summarising load status. No transformations occur at this stage.

**Run ID Format**: `YYYYMMDD_HHMMSS_#<hex>`

### 2. Silver Layer (Agentic Data Cleaning)

The silver layer uses **LLM agents** to automatically clean and standardize data:

#### **Silver Draft Agent** (`src/agents/load_2_silver_layer_draft_agent.py`)
- Analyzes Bronze data quality
- Identifies transformation needs
- Creates analysis reports

#### **Silver Builder Agent** (`src/agents/load_2_silver_layer_builder_agent.py`)
- Generates executable Python code
- Implements data cleaning logic
- Creates `src/runs/load_2_silver_layer.py`

#### **Silver Runner** (`src/runs/load_2_silver_layer.py`)
- Executes generated transformations:
  - Trims whitespace and converts empty strings to `NA`
  - Normalizes dates to ISO format (`YYYY-MM-DD`)
  - Parses numeric columns and converts identifiers to nullable integers
  - Harmonizes domain codes (e.g. gender values to `M`/`F`/`NA`)

**Run ID Logic**: Creates new run_id with fresh timestamp but same suffix as Bronze
- Bronze: `20260125_204110_#527f1cea`
- Silver: `20260125_204143_#527f1cea`

### 3. Gold Layer (Agentic Business Marts)

The gold layer uses **LLM agents** to build star‑schema data warehouses:

#### **Gold Draft Agent** (`src/agents/load_3_gold_layer_draft_agent.py`)
- Analyzes Silver data for business patterns
- Designs star schema architecture
- Plans dimension and fact tables

#### **Gold Builder Agent** (`src/agents/load_3_gold_layer_builder_agent.py`)
- Generates data mart creation code
- Implements star schema logic
- Creates `src/runs/load_3_gold_layer.py`

#### **Gold Runner** (`src/runs/load_3_gold_layer.py`)
- Creates business-ready data marts:
  - **Dimension tables** – customers, products and locations
  - **Fact table** – sales transactions
  - **Aggregated marts** – executive KPIs, performance metrics
  - **Wide tables** – enriched analytical views

**Run ID Logic**: Uses Bronze run_id for consistency across business marts

### 4. Business Insights Agent (`src/agents/business_insights_agent.py`)

Generates executive reports and business intelligence:
- Analyzes Gold data marts for KPIs
- Creates stakeholder-specific reports
- Generates visualizations and dashboards
- Produces C-level executive summaries

## Orchestration

The complete pipeline is orchestrated by `src/runs/orchestrator.py`:
- Validates environment and prerequisites
- Executes layers in sequence
- Handles failures and skip logic
- Generates comprehensive execution reports
- Manages run_id consistency across layers
