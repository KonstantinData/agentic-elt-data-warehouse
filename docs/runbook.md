# Runbook

This runbook provides instructions for running the agentic ELT pipeline locally, validating results and troubleshooting common issues. All commands are relative to the project root.

## Prerequisites

- **Python 3.8+** (tested with Python 3.12)
- **OpenAI API Key** (for LLM agents)
- **Git** for version control

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Setup

1. **Create virtual environment:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. **Setup environment variables:**
```bash
# Copy example environment file
cp configs\.env.example .env
# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_api_key_here
```

## Running the Pipeline

To execute the complete agentic ELT pipeline:

```bash
python .\src\runs\start_run.py
```

The pipeline will automatically:
1. **🥉 Bronze Layer** - Ingest raw CSV data
2. **🥈 Silver Layer** - LLM agents clean and standardize data
3. **🥇 Gold Layer** - LLM agents create business data marts
4. **📊 Business Insights** - Generate executive reports and visualizations

## Pipeline Output Structure

All outputs are organized by run ID:

```
artifacts/
├── bronze/YYYYMMDD_HHMMSS_#hash/     # Raw data snapshots
├── silver/YYYYMMDD_HHMMSS_#hash/      # Cleaned data (new timestamp, same suffix)
├── gold/marts/YYYYMMDD_HHMMSS_#hash/  # Business marts (Bronze run_id for consistency)
├── orchestrator/YYYYMMDD_HHMMSS_#hash/# Execution logs
└── reports/YYYYMMDD_HHMMSS_#hash/     # Summary reports
```

## Run ID Logic

- **Bronze**: Generates initial run_id (e.g., `20260125_204110_#527f1cea`)
- **Silver**: Creates new run_id with fresh timestamp but same suffix (e.g., `20260125_204143_#527f1cea`)
- **Gold**: Uses Bronze run_id for mart consistency
- **Reports**: Use orchestrator run_id

## Validating Results

The repository includes a comprehensive test suite:

```bash
pytest -q
```

Tests include:
- Unit tests for transformations
- Contract tests for output artifacts
- Integration tests for end-to-end pipeline
- Quality tests for generated code

## Troubleshooting

### Common Issues

**Missing OpenAI API Key:**
```
RuntimeError: Missing OPEN_AI_KEY or OPENAI_API_KEY in .env
```
Solution: Add your OpenAI API key to `.env` file

**Missing raw data:**
```
FileNotFoundError: Missing required raw source directories
```
Solution: Ensure `raw/source_crm` and `raw/source_erp` contain CSV files

**Permission errors:**
```
PermissionError: [Errno 13] Permission denied
```
Solution: Check write permissions to `artifacts/` directory

**Agent failures:**
- Check `artifacts/orchestrator/*/logs/` for detailed error logs
- Verify OpenAI API key has sufficient credits
- Review LLM agent context in `tmp/draft_reports/`

### Pipeline Options

**Skip LLM agents (for testing):**
```bash
python .\src\runs\start_run.py --skip-llm
```

**Custom run ID:**
```bash
set ORCHESTRATOR_RUN_ID=custom_run_id
python .\src\runs\start_run.py
```

### Incremental Processing

The pipeline automatically detects unchanged raw data and skips processing when no new data is available, saving time and resources.

### Getting Help

- Check execution logs in `artifacts/orchestrator/*/logs/`
- Review agent context in `tmp/draft_reports/`
- Enable debug logging by setting `LOG_LEVEL=DEBUG` in `.env`
- Check existing [Issues](https://github.com/YOUR_USERNAME/agentic-elt-data-warehouse/issues)
