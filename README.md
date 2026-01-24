# Agentic ELT Data Warehouse

This repository contains an agentic ELT/analytics pipeline that uses LLM agents to generate and execute data transformation code.

## Running the Pipeline

To execute the full pipeline, run:

```bash
python .\src\runs\start_run.py
```

This will:
1. **Bronze layer** – ingest raw CSV files
2. **Silver layer** – clean and standardize data using LLM-generated code
3. **Gold layer** – build business marts using LLM-generated transformations
4. **Summary report** – generate execution summary

## Output Structure

Pipeline outputs are stored in:
- `artifacts/bronze/<run_id>/` – raw data copies
- `artifacts/silver/<run_id>/` – cleaned data
- `artifacts/gold/marts/<run_id>/` – business marts
- `artifacts/orchestrator/<run_id>/logs/` – execution logs
- `artifacts/reports/<run_id>/` – summary reports

## Requirements

- Python 3.8+
- OpenAI API key in `.env` file
- Raw data in `raw/source_crm/` and `raw/source_erp/`

## Running Tests

```bash
pytest -q
```