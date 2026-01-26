# Agentic ELT Data Warehouse

🇩🇪 **[Deutsche Version / German Version](README_de.md)**

This repository contains a production-ready agentic ELT/analytics pipeline that uses LLM agents to automatically generate and execute data transformation code. The system demonstrates how AI can be integrated into traditional data engineering workflows to create self-adapting data pipelines.

## 🚀 Quick Start

### Fork & Clone
1. Fork this repository to your GitHub account
2. Clone your fork locally:
```bash
git clone https://github.com/YOUR_USERNAME/agentic-elt-data-warehouse.git
cd agentic-elt-data-warehouse
```

### Prerequisites
- **Python 3.8+** (tested with Python 3.12)
- **OpenAI API Key** (for LLM agents)
- **Git** for version control

### Installation

1. **Create virtual environment:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Setup environment variables:**
```bash
# Copy example environment file
cp configs\.env.example .env
# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_api_key_here
```

### Sample Dataset
The repository includes a complete sample dataset in `raw/` directory:
- **CRM data** (`raw/source_crm/`): Customer information, product details, sales data
- **ERP data** (`raw/source_erp/`): Additional customer data, location info, product categories, transactions

This synthetic dataset represents a typical mid-sized company's data structure and is ready to use out-of-the-box.

## 🏃‍♂️ Running the Pipeline

Execute the complete ELT pipeline:
```bash
python .\src\runs\start_run.py
```

### What Happens
The pipeline executes these steps automatically:

1. **🥉 Bronze Layer** - Raw data ingestion
   - Copies CSV files from `raw/` directories
   - Validates data integrity with checksums
   - Creates immutable snapshots

2. **🥈 Silver Layer** - Data cleaning & standardization
   - LLM agents analyze data quality issues
   - Generate Python code for data cleaning
   - Execute transformations automatically
   - Handle missing values, data types, formatting

3. **🥇 Gold Layer** - Business marts creation
   - LLM agents design star schema
   - Generate dimension and fact tables
   - Create business KPI aggregations
   - Build analytics-ready datasets

4. **📊 Summary Report** - Execution summary
   - Pipeline execution metrics
   - Data quality assessments
   - Generated code documentation

## 📈 Running the Dashboard

### Streamlit overview

The multipage UI is powered by Streamlit (`src/dashboard/app.py`) and reads the latest Silver artifacts that the ELT pipeline writes to `artifacts/runs/<run_id>/silver/data/`. The dashboard lists all available runs, keeps sidebar filters (dates, product lines, countries, genders, etc.) in session state, and reloads datasets automatically whenever you switch the selected run. Each page—from the Executive Overview down to the diagnostics and export views—reuses shared components that persist filters, summarize change signals, and make the current context ready for download.

### Start the Streamlit dashboard

Start the dashboard once at least one Silver run has completed:

#### Windows

```powershell
scripts\run_dashboard.ps1
```

#### Linux/macOS

```bash
./scripts/run_dashboard.sh
```

Alternatively, run Streamlit directly so you can pass CLI flags:

```bash
python -m streamlit run src/dashboard/app.py
```

The dashboard discovers artifacts under `artifacts/runs/<run_id>/silver/data/` (with a safe fallback to `artifacts/silver/<run_id>/data/`). If no runs are available it will prompt you to execute the pipeline first. The first run in the sidebar is always the most recent finish, but you can switch to any earlier run to compare results.

### Streamlit insights

- **Executive Overview (pages/01)** surfaces KPI cards, trend charts, product mix maps, order signal charts, and the diagnostics summary that glue together the most important metrics from the selected Silver run.
- **Exploration sandbox (pages/02)** exposes a live dataframe preview plus top-products, top-countries, and top-customers tables so you can validate transformation logic without leaving Streamlit.
- **Run diagnostics (pages/03)** mirrors the metadata, logging, and missingness checks that the pipeline captures and feeds that data into an expandable diagnostics panel.
- **Exports & context (pages/04)** lets you download the filtered dataset as CSV plus a JSON payload of the active filters, run ID, and artifact source for audit-ready sharing.
- The sidebar filters are configured and persisted via `src/dashboard/components/filters.py`, so the date range, product keys, gender, and country selections are reused across pages until you reset them.

### Streamlit configuration and tips

- `.streamlit/config.toml` defines the light/dark theme palette; adjust those values if you want a custom brand look for your dashboard.
- The Streamlit CLI can be tweaked via environment variables such as `STREAMLIT_SERVER_PORT` or `STREAMLIT_BROWSER_GATHER_USAGE_STATS` if the default port is blocked or you want to disable usage reporting.
- Because the dashboard loads persisted datasets, rerun `python .\src\runs\start_run.py` (or the orchestrator) before launching Streamlit whenever you refresh the raw data; stale runs will be marked with guidance text instead of charts.
- Use the provided `scripts/run_dashboard.*` wrappers to keep the command consistent across operating systems, or pass `--server.headless true` / `--server.address` arguments directly to `python -m streamlit run` when you host the dashboard.

## 📁 Output Structure

All pipeline outputs are organized by run ID:

```
artifacts/
├── bronze/YYYYMMDD_HHMMSS_#hash/     # Raw data snapshots
│   ├── data/*.csv                     # Copied source files
│   └── reports/elt_report.html        # Ingestion report
├── silver/YYYYMMDD_HHMMSS_#hash/      # Cleaned data
│   ├── data/*.csv                     # Standardized tables
│   └── reports/elt_report.html        # Quality report
├── gold/marts/YYYYMMDD_HHMMSS_#hash/  # Business marts
│   ├── data/*.csv                     # Star schema tables
│   └── reports/gold_report.html       # Marts documentation
├── orchestrator/YYYYMMDD_HHMMSS_#hash/# Execution logs
│   └── logs/*.log                     # Detailed step logs
└── reports/YYYYMMDD_HHMMSS_#hash/     # Summary reports
    ├── summary_report.md              # Human-readable summary
    └── summary_report.json            # Machine-readable metrics
```

## 🔧 Configuration Options

### Incremental Processing
The pipeline automatically detects unchanged raw data and skips processing when no new data is available. This saves time and resources on subsequent runs with identical input files.

### Environment Variables
Key configuration in `.env`:
```bash
OPENAI_API_KEY=your_key_here          # Required for LLM agents
ORCHESTRATOR_RUN_ID=custom_run_id     # Optional: custom run identifier
```

## 🧪 Testing

Run the complete test suite:
```bash
pytest -q
```

Test categories:
- **Unit tests** - Individual component testing
- **Integration tests** - End-to-end pipeline validation
- **Contract tests** - Data schema validation
- **Quality tests** - Code quality and documentation

## 🏗️ Architecture

### Agentic Components
- **Draft Agents** - Analyze data and generate transformation code
- **Builder Agents** - Refine and optimize generated code
- **Quality Agents** - Validate code quality and performance

### Data Flow
```
Raw Data → Bronze (Ingestion) → Silver (Cleaning) → Gold (Business Logic) → Reports
     ↓           ↓                    ↓                    ↓
   LLM Analysis → Code Generation → Execution → Validation
```

### Key Features
- **Deterministic execution** - Same inputs produce identical outputs
- **Audit trail** - Complete lineage tracking
- **Error handling** - Graceful failure recovery
- **Incremental processing** - Skip unchanged data
- **GDPR compliance** - PII handling and pseudonymization

## 📊 Sample Data Overview

The included dataset simulates:
- **~1000 customers** across multiple segments
- **~50 products** in various categories
- **~5000 sales transactions** over time periods
- **Multiple data quality issues** for testing cleanup logic

Data includes intentional quality issues:
- Missing values
- Inconsistent formatting
- Duplicate records
- Data type mismatches

## 🔍 Monitoring & Observability

Each run generates comprehensive monitoring data:
- **Execution metrics** - Runtime, memory usage, success rates
- **Data quality scores** - Completeness, validity, consistency
- **Code generation logs** - LLM interactions and decisions
- **Error tracking** - Detailed failure analysis

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**Missing OpenAI API Key:**
```
RuntimeError: Missing OPEN_AI_KEY or OPENAI_API_KEY in .env
```
Solution: Add your OpenAI API key to `.env` file

**Import Errors:**
```
ModuleNotFoundError: No module named 'xyz'
```
Solution: Ensure virtual environment is activated and dependencies installed

**Permission Errors:**
```
PermissionError: [Errno 13] Permission denied
```
Solution: Check file permissions and ensure write access to `artifacts/` directory

### Getting Help
- Check existing [Issues](https://github.com/YOUR_USERNAME/agentic-elt-data-warehouse/issues)
- Review execution logs in `artifacts/orchestrator/*/logs/`
- Enable debug logging by setting `LOG_LEVEL=DEBUG` in `.env`

---

**Ready to see AI-powered data engineering in action? Run `python .\src\runs\start_run.py` and watch the magic happen! ✨**
