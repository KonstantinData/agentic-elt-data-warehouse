# Agentic ELT Data Warehouse

🇩🇪 **[Deutsche Version](README_de.md)**

This repository contains a production-ready agentic ELT/analytics pipeline that uses LLM agents to automatically generate and execute data transformation code. The system demonstrates how AI can be integrated into traditional data engineering workflows to create self-adapting data pipelines.

## 🚀 Quickstart

### Fork & Clone

1. Fork this repository to your GitHub account
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/agentic-elt-data-warehouse.git
cd agentic-elt-data-warehouse
```

### Prerequisites

- **Python 3.8+** (tested with Python 3.12)
- **OpenAI API Key** (for the LLM agents)
- **Git** for version control

### Installation

1. **Create a virtual environment:**

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

3. **Set up environment variables:**

```bash
# Copy the example environment file
cp configs\.env.example .env
# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_api_key_here
```

### Sample dataset

The repository includes a complete sample dataset in the `raw/` directory:

- **CRM data** (`raw/source_crm/`): customer information, product details, sales data
- **ERP data** (`raw/source_erp/`): additional customer data, location information, product categories, transactions

This synthetic dataset represents the data structure of a typical mid-sized company and is ready to use out of the box.

## 🏃‍♂️ Run the pipeline

Run the full ELT pipeline:

```bash
python .\src\runs\start_run.py
```

### What happens

The pipeline automatically performs these steps:

1. **🥉 Bronze layer** – raw ingestion

   - Copies CSV files from the `raw/` directories
   - Validates data integrity with checksums
   - Creates immutable snapshots
2. **🥈 Silver layer** – cleaning & standardization

   - LLM agents analyze data quality issues
   - Generate Python code for cleaning
   - Execute transformations automatically
   - Handle missing values, data types, formatting
3. **🥇 Gold layer** – business marts

   - LLM agents design a star schema
   - Generate dimension and fact tables
   - Create business KPI aggregations
   - Build analytics-ready datasets
4. **📊 Summary report** – execution overview

   - Pipeline execution metrics
   - Data quality assessments
   - Generated code documentation

## 📈 Run the dashboard

### Streamlit overview

The multi-page dashboard is built with Streamlit (`src/dashboard/app.py`) and loads the latest Silver artifacts from `artifacts/runs/<run_id>/silver/data/`. It lists all available runs, stores sidebar filters (date, product lines, countries, gender, etc.) in session state, and reloads datasets as soon as a different run is selected. Each page—from Executive Overview to diagnostics and exports—uses shared components to persist filters and provide the current context for downloads.

### Start the dashboard

Start the dashboard once at least one Silver run has completed:

#### Windows

```powershell
scripts\run_dashboard.ps1
```

#### Linux/macOS

```bash
./scripts/run_dashboard.sh
```

Alternatively, you can start Streamlit directly to pass CLI flags:

```bash
python -m streamlit run src/dashboard/app.py
```

The dashboard discovers artifacts under `artifacts/runs/<run_id>/silver/data/` (with a safe fallback to `artifacts/silver/<run_id>/data/`). If no runs are found, it prompts you to run the pipeline first. The initially selected run is always the most recently completed one, but you can choose any older run for comparison.

### Streamlit insights

- **Executive Overview (pages/01)** shows KPI cards, trend charts, product-mix maps, order signals, and a diagnostics panel that consolidates the key metrics of the selected Silver run.
- **Exploration Sandbox (pages/02)** provides an interactive preview of the filtered data as well as tables for top products, top countries, and top customers so you can validate transformation logic right in the dashboard.
- **Run Diagnostics (pages/03)** mirrors metadata, log information, and missing values captured by the pipeline and presents them in an expandable panel.
- **Exports & Context (pages/04)** lets you download the filtered dataset as CSV and a JSON bundle containing active filters, run ID, and artifact source for audit purposes.
- Sidebar filters are configured via `src/dashboard/components/filters.py` and persist until you reset them.

### Streamlit configuration and tips

- `.streamlit/config.toml` defines the light/dark themes and can be adjusted if you need a custom color scheme.
- CLI options can be controlled via environment variables such as `STREAMLIT_SERVER_PORT` or `STREAMLIT_BROWSER_GATHER_USAGE_STATS`—for example if the default port is blocked or you want to disable usage stats.
- Before restarting the Streamlit dashboard, run `python .\src\runs\start_run.py` (or the orchestrator) again so fresh Silver artifacts are available; otherwise, older runs show explanatory hint text.
- Use the scripts `scripts/run_dashboard.ps1`/`.sh` to keep the command consistent across operating systems, or pass flags like `--server.headless true` or `--server.address` to `python -m streamlit run` when hosting the dashboard.

## 📁 Output structure

All pipeline outputs are organized by run ID:

```
artifacts/
├── bronze/YYYYMMDD_HHMMSS_#hash/     # Raw snapshots
│   ├── data/*.csv                     # Copied source files
│   └── reports/elt_report.html        # Ingestion report
├── silver/YYYYMMDD_HHMMSS_#hash/      # Cleaned data
│   ├── data/*.csv                     # Standardized tables
│   └── reports/elt_report.html        # Quality report
├── gold/marts/YYYYMMDD_HHMMSS_#hash/  # Business marts
│   ├── data/*.csv                     # Star-schema tables
│   └── reports/gold_report.html       # Marts documentation
├── orchestrator/YYYYMMDD_HHMMSS_#hash/# Execution logs
│   └── logs/*.log                     # Detailed step logs
└── reports/YYYYMMDD_HHMMSS_#hash/     # Summary reports
    ├── summary_report.md              # Human-readable summary
    └── summary_report.json            # Machine-readable metrics
```

## 🔧 Configuration options

### Incremental processing

The pipeline automatically detects unchanged raw inputs and skips processing if no new data is available. This saves time and resources on subsequent runs with identical input files.

### Environment variables

Key configuration in `.env`:

```bash
OPENAI_API_KEY=your_key_here          # Required for LLM agents
ORCHESTRATOR_RUN_ID=custom_run_id     # Optional: custom run ID
```

## 🧪 Testing

Run the full test suite:

```bash
pytest -q
```

Test categories:

- **Unit tests** – component-level tests
- **Integration tests** – end-to-end pipeline validation
- **Contract tests** – data schema validation
- **Quality tests** – code quality and documentation

## 🏗️ Architecture

### Agentic components

- **Draft Agents** – analyze data and generate transformation code
- **Builder Agents** – refine and optimize generated code
- **Quality Agents** – validate code quality and performance

### Data flow

```
Raw data → Bronze (ingestion) → Silver (cleaning) → Gold (business logic) → Reports
     ↓           ↓                    ↓                    ↓
  LLM analysis → Code generation → Execution → Validation
```

### Key features

- **Deterministic execution** – identical inputs produce identical outputs
- **Audit trail** – full lineage tracking
- **Error handling** – graceful recovery
- **Incremental processing** – skip unchanged data
- **Privacy & governance** – PII detection, pseudonymization/redaction, minimal prompt/log footprint (see “Privacy & EU AI Act”)

## 🔐 Privacy & EU AI Act (EU/DE)

> Note: This section provides practical guidance and is **not legal advice**. Validate requirements with your Data Protection Officer and (if needed) legal counsel.

This project ships with **synthetic sample data**. As soon as you process real data (especially customer, employee, or transaction data), you typically need to comply with **GDPR** and—depending on the use case—requirements under the **EU AI Act**.

### GDPR: typical obligations for LLM-assisted data analysis

- **Data classification & PII**: Identify personal data (direct/indirect) and sensitive/special-category data (e.g., health, union membership, biometric).
- **Legal basis & purpose limitation**: Document purpose and legal basis (Art. 6 GDPR) and, where applicable, Art. 9 GDPR.
- **Processor agreements**: With external LLM providers, you usually need a **data processing agreement** (Art. 28 GDPR), including a sub-processor list.
- **International transfers**: If processing may occur outside the EU/EEA, ensure appropriate safeguards (e.g., SCCs) and assess transfer risks.
- **Privacy by design**: Data minimization, pseudonymization/anonymization, access controls, encryption, and logging only when necessary.
- **Deletion & retention**: Define retention for artifacts/logs (including prompt/response logs).
- **DPIA**: Consider/assess a Data Protection Impact Assessment for high-risk processing (e.g., profiling, large volumes, sensitive data).

### Recommended technical measures in this pipeline

- **Do not send raw PII to the LLM**: Reduce inputs to what is strictly necessary (e.g., schema/statistics instead of raw rows).
- **Pseudonymize before LLM steps**: Hash/tokenize stable identifiers (e.g., `customer_id`), mask free-text fields.
- **Prompt/log redaction**: If LLM interactions are logged, remove PII consistently; restrict access to logs.
- **Secrets handling**: Store API keys only in `.env`/a secret store—never commit them.
- **Protect artifacts**: `artifacts/` may contain analyzable data—treat the directory like production data (permissions, encryption, retention).

### EU AI Act: when does it matter?

The EU AI Act is **risk-based**. For purely internal analytics assistance, it is often *not* considered “high-risk”. It can become **high-risk** if model outputs feed into decisions about people (e.g., HR, creditworthiness/scoring, access to services) or if the use case is regulated.

Practical minimum measures you should document in the project:

- **Intended use** (purpose & limits): What the system may be used for—and what it must not be used for.
- **Human oversight**: Who reviews critical outputs before they are operationalized?
- **Quality & monitoring**: Validation (hallucinations, data quality), tests, drift/error monitoring.
- **Transparency**: Label AI-assisted content/decision rationales where required.

### Short checklist before production use

- [ ] PII/special categories identified and minimized
- [ ] Processor agreement / sub-processors / transfer mechanisms reviewed
- [ ] Retention/deletion policy for `artifacts/` and logs defined
- [ ] Prompt/log redaction or “no logging” implemented
- [ ] Intended use + human-in-the-loop documented for critical use cases

## 📊 Sample data overview

The included dataset simulates:

- **~1,000 customers** across multiple segments
- **~50 products** across different categories
- **~5,000 sales transactions** over time
- **Multiple data quality issues** to test cleaning logic

Data includes intentional quality issues:

- Missing values
- Inconsistent formatting
- Duplicate records
- Data type mismatches

## 🔍 Monitoring & Observability

Each run generates comprehensive monitoring data:

- **Execution metrics** – runtime, memory usage, success rates
- **Data quality scores** – completeness, validity, consistency
- **Code generation logs** – LLM interactions and decisions
- **Error tracking** – detailed error analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to your branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common issues

**Missing OpenAI API key:**

```
RuntimeError: Missing OPEN_AI_KEY or OPENAI_API_KEY in .env
```

Fix: add your OpenAI API key to the `.env` file

**Import error:**

```
ModuleNotFoundError: No module named 'xyz'
```

Fix: ensure the virtual environment is activated and dependencies are installed

**Permission error:**

```
PermissionError: [Errno 13] Permission denied
```

Fix: check file permissions and ensure you have write access to the `artifacts/` directory

### Getting help

- Check existing [Issues](https://github.com/YOUR_USERNAME/agentic-elt-data-warehouse/issues)
- Review execution logs in `artifacts/orchestrator/*/logs/`
- Enable debug logging by setting `LOG_LEVEL=DEBUG` in `.env`

---

**Ready to see AI-powered data engineering in action? Run `python .\src\runs\start_run.py` and experience the magic! ✨**
