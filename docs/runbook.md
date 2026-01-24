# Runbook

This runbook provides instructions for running the pipeline locally, validating results and troubleshooting common issues.  All commands are relative to the project root.

## Prerequisites

- Python ≥3.10 (tested with CPython 3.10 and 3.11)
- Virtualenv or `pipenv` for dependency isolation (optional)
- Jupyter (for executing notebooks)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Pipeline

To execute the full pipeline end‑to‑end and produce a fresh run, run:

```bash
python src/pipeline/golden_path.py --seed 42
```

You can optionally specify a custom run identifier:

```bash
python src/pipeline/golden_path.py --run-id 20260124_123456_#abcd1234 --seed 42
```

After completion the final exposé is located at:

```
artifacts/runs/<run_id>/reports/final_expose.md
```

## Validating Results

The repository includes a comprehensive test suite in the `tests/` folder.  To run tests locally:

```bash
pytest -q
```

Tests include unit tests for transformations, contract tests ensuring output artefacts exist and contain expected content, deterministic seeding tests and an end‑to‑end smoke test on sample fixture data.  CI workflows execute these tests automatically.

## Troubleshooting

1. **Missing raw data** – Ensure the folders `raw/source_crm` and `raw/source_erp` exist and contain CSV files.  Without raw data the bronze loader will raise a `FileNotFoundError`.
2. **Permission errors** – The pipeline writes to `artifacts/runs/`.  Check that the user running the command has write permissions to that directory.
3. **Invalid run id** – Run identifiers must match the pattern `YYYYMMDD_HHMMSS_#<hex>`.  If you supply a custom id make sure it conforms to this format.
4. **Non‑deterministic results** – Always supply the same `--seed` to reproduce identical outputs.  Changing the seed will change the clustering results.
5. **CI failures** – The CI workflow enforces placeholder scans, notebook execution and code documentation compliance.  Examine the CI logs to identify which gate failed and fix the offending code or documentation.
